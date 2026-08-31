#!/usr/bin/env python3
"""Run the fixed 10-video Sera transcript acquisition benchmark.

The runner is intentionally acquisition-only. It writes resumable, sanitized
attempt artifacts and never persists API keys, cookies, signed audio URLs, or
temporary media.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import requests


VIDEO_IDS = [
    "27t1tZaNsdU",
    "eEp47vWKUB8",
    "KH3mi2h8vw8",
    "-vLc3qXoVBs",
    "3GmlSvWFEDE",
    "Lw-0bdr7yk0",
    "tx0JT4ie_aw",
    "hdzWq6k0xm0",
    "_tpvhmZvR0A",
    "0lzcNMe5dOk",
]

PROVIDERS = [
    "supadata",
    "scrapecreators",
    "apify",
    "firecrawl_transcript",
    "jina",
    "local_youtube_transcript_api",
    "local_ytdlp_caption",
    "firecrawl_audio",
    "local_audio_asr",
]

PROVIDER_LABELS = {
    "supadata": "Supadata",
    "scrapecreators": "ScrapeCreators",
    "apify": "Apify",
    "firecrawl_transcript": "Firecrawl transcript",
    "jina": "Jina Reader",
    "local_youtube_transcript_api": "youtube-transcript-api",
    "local_ytdlp_caption": "yt-dlp captions",
    "firecrawl_audio": "Firecrawl audio + ASR",
    "local_audio_asr": "Local yt-dlp audio + ASR",
}

DEFAULT_CATALOG = Path(os.environ.get("SERA_CREATOR_CATALOG", "database/videos.json"))
DEFAULT_OUTPUT = Path(os.environ.get("SERA_CREATOR_BENCHMARK_OUTPUT", "benchmark-output"))
DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "transcript-acquisition.schema.json"
YTDLP = Path(os.environ.get("YTDLP_BIN") or shutil.which("yt-dlp") or "yt-dlp")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36"
LANGS = ["zh-Hans", "zh-Hant", "zh-CN", "zh-TW", "zh", "en"]
YTDLP_COMMON = [
    "--no-warnings",
    "--ignore-errors",
    "--socket-timeout", "25",
    "--retries", "3",
    "--cookies-from-browser", "edge",
    "--extractor-args", "youtube:player_client=web_embedded",
    "--ignore-no-formats-error",
    "--remote-components", "ejs:github",
]
CSV_FIELDS = [
    "video_id", "title", "provider", "source_kind", "configured", "attempted",
    "status", "failure_taxonomy", "http_status", "latency_ms", "cost_units",
    "language", "segment_count", "text_length", "timestamp_coverage",
    "estimated_content_coverage", "suspected_mismatch", "error_class",
    "error_message", "retrieved_at", "normalized_path", "raw_path",
]

SIGNED_URL_RE = re.compile(r"https?://[^\s\"']+(?:googlevideo|X-Amz-|Signature=)[^\s\"']*", re.I)
TIMESTAMP_RE = re.compile(
    r"(?m)^\s*(?:\[|\()?((?:\d{1,2}:)?\d{1,2}:\d{2})(?:\.\d+)?(?:\]|\))?\s*[-:]?\s*(.*)$"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def discover_env_files(explicit: list[Path]) -> list[Path]:
    candidates = list(explicit)
    home = Path.home()
    for root in (home / ".config", home / "projects", home / "Projects"):
        if not root.exists():
            continue
        for pattern in (".env", ".env.*", "*.env"):
            candidates.extend(path for path in root.rglob(pattern) if path.is_file() and path.stat().st_size <= 1_000_000)
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.expanduser().resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def load_env_value(name: str, env_files: list[Path]) -> str | None:
    value = os.environ.get(name)
    if value:
        return value.strip()
    for path in env_files:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if line.startswith("export "):
                line = line[7:].strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, candidate = line.split("=", 1)
            if key.strip() == name:
                return candidate.strip().strip("\"'") or None
    return None


def detect_proxy_url() -> str | None:
    for name in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        value = os.environ.get(name)
        if value:
            return value.strip()
    try:
        result = subprocess.run(
            ["scutil", "--proxy"], text=True, capture_output=True, timeout=10, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    values: dict[str, str] = {}
    for raw in result.stdout.splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        values[key.strip()] = value.strip()
    if values.get("HTTPSEnable") != "1":
        return None
    host = values.get("HTTPSProxy")
    port = values.get("HTTPSPort")
    if not host or not port:
        return None
    return f"http://{host}:{port}"


def redact_text(value: Any, secrets: list[str]) -> str:
    text = str(value or "").replace("\n", " ").strip()
    text = SIGNED_URL_RE.sub("[redacted-signed-url]", text)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[redacted-secret]")
    return text


def clean_error(value: Any, secrets: list[str]) -> str:
    return redact_text(value, secrets)[:1000]


def sanitized(value: Any, secrets: list[str]) -> Any:
    if isinstance(value, dict):
        return {key: sanitized(item, secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitized(item, secrets) for item in value]
    if isinstance(value, str):
        return redact_text(value, secrets)
    return value


def parse_seconds(value: str) -> float:
    parts = [float(part) for part in value.split(":")]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return parts[0] * 60 + parts[1]


def parse_vtt(path: Path) -> list[dict[str, Any]]:
    time_re = re.compile(
        r"(?:(\d+):)?(\d{2}):(\d{2}[.,]\d{3})\s+-->\s+"
        r"(?:(\d+):)?(\d{2}):(\d{2}[.,]\d{3})"
    )
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    segments: list[dict[str, Any]] = []
    seen: set[tuple[float, str]] = set()
    i = 0
    while i < len(lines):
        match = time_re.search(lines[i])
        if not match:
            i += 1
            continue
        sh, sm, ss, eh, em, es = match.groups()
        start = int(sh or 0) * 3600 + int(sm) * 60 + float(ss.replace(",", "."))
        end = int(eh or 0) * 3600 + int(em) * 60 + float(es.replace(",", "."))
        i += 1
        rows: list[str] = []
        while i < len(lines) and lines[i].strip():
            row = re.sub(r"<[^>]+>", "", lines[i])
            row = html.unescape(row).strip()
            if row and not row.startswith(("Kind:", "Language:")):
                rows.append(row)
            i += 1
        text = re.sub(r"\s+", " ", " ".join(rows)).strip()
        key = (round(start, 3), text)
        if text and key not in seen:
            seen.add(key)
            segments.append({"start": start, "end": max(start, end), "text": text})
    return segments


def extract_web_transcript(markdown: str) -> list[dict[str, Any]]:
    lowered = markdown.lower()
    transcript_signal = any(
        token in lowered for token in ("transcript", "show transcript", "\u6587\u5b57\u7a3f", "\u8f6c\u5f55", "\u8f49\u9304")
    )
    matches = list(TIMESTAMP_RE.finditer(markdown))
    if not transcript_signal or len(matches) < 5:
        return []
    segments: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = parse_seconds(match.group(1))
        inline = match.group(2).strip()
        following = markdown[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(markdown)]
        rows = [inline] if inline else []
        rows.extend(row.strip() for row in following.splitlines() if row.strip())
        text = re.sub(r"\s+", " ", " ".join(rows)).strip(" #-*")
        if not text:
            continue
        end = parse_seconds(matches[index + 1].group(1)) if index + 1 < len(matches) else start + 5.0
        segments.append({"start": start, "end": max(start, end), "text": text})
    if len(segments) < 5 or sum(len(item["text"]) for item in segments) < 300:
        return []
    return segments


def full_text(segments: list[dict[str, Any]]) -> str:
    return "\n".join(str(item.get("text") or "").strip() for item in segments if str(item.get("text") or "").strip())


def language_plausible(language: str | None, text: str) -> bool:
    if language:
        normalized = language.lower().replace("_", "-")
        if normalized.startswith(("zh", "cmn", "yue", "en")):
            return True
        return False
    if not text:
        return False
    cjk = len(re.findall(r"[\u3400-\u9fff]", text[:4000]))
    latin = len(re.findall(r"[A-Za-z]", text[:4000]))
    return cjk >= 20 or latin >= 50


def quality_for(
    meta: dict[str, Any],
    segments: list[dict[str, Any]],
    language: str | None,
    returned_video_id: str | None,
    identity_is_requested_url: bool = False,
) -> tuple[dict[str, Any], dict[str, bool | None]]:
    text = full_text(segments)
    duration = float(meta.get("duration") or 0)
    last_end = max((float(item.get("end") or 0) for item in segments), default=0.0)
    timestamped = sum(
        1 for item in segments
        if isinstance(item.get("start"), (int, float)) and isinstance(item.get("end"), (int, float))
        and float(item["end"]) >= float(item["start"])
    )
    timestamp_coverage = timestamped / len(segments) if segments else 0.0
    coverage = min(1.0, last_end / duration) if duration and last_end else 0.0
    id_match: bool | None
    if returned_video_id:
        id_match = returned_video_id == meta["video_id"]
    elif identity_is_requested_url:
        id_match = True
    else:
        id_match = None
    duration_plausible = None if not duration or not last_end else 0.45 <= last_end / duration <= 1.35
    lang_ok = language_plausible(language, text)
    checks: dict[str, bool | None] = {
        "video_id_match": id_match,
        "duration_plausible": duration_plausible,
        "language_plausible": lang_ok,
    }
    suspected = id_match is False or duration_plausible is False or not lang_ok
    return {
        "timestamp_coverage": round(timestamp_coverage, 4),
        "coverage": round(coverage, 4),
        "timestamp_quality": "full" if timestamp_coverage >= 0.95 else "partial" if timestamp_coverage else "none",
        "language_match": lang_ok,
        "suspected_mismatch": suspected,
    }, checks


def classify_failure(http_status: int | None, message: str) -> str:
    lower = message.lower()
    if http_status in (401, 402) or "unauthorized" in lower or "api key" in lower:
        return "auth_error"
    if http_status == 429 or "rate limit" in lower or "quota" in lower:
        return "rate_limited"
    if http_status == 404 or "not found" in lower or "video unavailable" in lower:
        return "not_found"
    if http_status == 403 or any(token in lower for token in ("confirm you're not a bot", "requestblocked", "blocked")):
        return "blocked"
    if "timed out" in lower or "timeout" in lower:
        return "timeout"
    if "no transcript" in lower or "transcriptsdisabled" in lower or "no caption" in lower:
        return "no_transcript"
    if http_status and 400 <= http_status < 500:
        return "bad_request"
    return "provider_error"


def normalized_attempt_status(record: dict[str, Any]) -> str:
    if record["status"] == "success":
        return "success"
    if record["status"] == "not_configured":
        return "not_configured"
    taxonomy = record.get("failure_taxonomy")
    if taxonomy == "content_mismatch":
        return "mismatch"
    if taxonomy == "no_transcript":
        return "empty"
    if taxonomy in {"blocked", "rate_limited", "auth_error", "timeout"}:
        return taxonomy
    return "provider_error"


class Benchmark:
    def __init__(self, args: argparse.Namespace) -> None:
        self.output = args.output.resolve()
        self.catalog_path = args.catalog.resolve()
        self.schema_path = args.schema.resolve()
        self.env_files = discover_env_files(args.env_file)
        self.model_name = args.model
        self.force = args.force
        self.selected = set(args.providers.split(",") if args.providers else PROVIDERS)
        unknown = self.selected.difference(PROVIDERS)
        if unknown:
            raise ValueError(f"unknown providers: {', '.join(sorted(unknown))}")
        self.output.mkdir(parents=True, exist_ok=True)
        (self.output / "raw").mkdir(exist_ok=True)
        self.state_path = self.output / "_state.json"
        self.catalog = self._load_catalog()
        self.proxy_url = detect_proxy_url()
        if self.proxy_url:
            os.environ.setdefault("HTTP_PROXY", self.proxy_url)
            os.environ.setdefault("HTTPS_PROXY", self.proxy_url)
            os.environ.setdefault("http_proxy", self.proxy_url)
            os.environ.setdefault("https_proxy", self.proxy_url)
        self.http = requests.Session()
        if self.proxy_url:
            self.http.proxies.update({"http": self.proxy_url, "https": self.proxy_url})
        self.keys = {
            "scrapecreators": load_env_value("SCRAPECREATORS_API_KEY", self.env_files),
            "firecrawl": load_env_value("FIRECRAWL_API_KEY", self.env_files),
            "supadata": load_env_value("SUPADATA_API_KEY", self.env_files),
            "apify": load_env_value("APIFY_API_TOKEN", self.env_files),
            "jina": load_env_value("JINA_API_KEY", self.env_files),
        }
        self.secrets = [value for value in self.keys.values() if value]
        self.records: dict[str, dict[str, Any]] = self._load_state()
        self.whisper: Any = None

    def _load_catalog(self) -> dict[str, dict[str, Any]]:
        data = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        index = {item["video_id"]: item for item in data["videos"]}
        missing = [video_id for video_id in VIDEO_IDS if video_id not in index]
        if missing:
            raise ValueError(f"catalog missing fixed IDs: {missing}")
        return {video_id: index[video_id] for video_id in VIDEO_IDS}

    def _load_state(self) -> dict[str, dict[str, Any]]:
        if not self.state_path.exists():
            return {}
        data = json.loads(self.state_path.read_text(encoding="utf-8"))
        if data.get("video_ids") != VIDEO_IDS:
            raise ValueError("existing state does not match fixed 10-video sample")
        return {f"{item['provider']}::{item['video_id']}": item for item in data.get("records", [])}

    def configured(self, provider: str) -> bool:
        if provider == "supadata":
            return bool(self.keys["supadata"])
        if provider == "scrapecreators":
            return bool(self.keys["scrapecreators"])
        if provider == "apify":
            return bool(self.keys["apify"])
        if provider.startswith("firecrawl"):
            return bool(self.keys["firecrawl"])
        return True

    def base_record(self, provider: str, meta: dict[str, Any]) -> dict[str, Any]:
        return {
            "video_id": meta["video_id"],
            "title": meta.get("title"),
            "provider": provider,
            "source_kind": None,
            "configured": self.configured(provider),
            "attempted": False,
            "status": "not_configured" if not self.configured(provider) else "failed",
            "failure_taxonomy": None,
            "http_status": None,
            "latency_ms": None,
            "cost_units": None,
            "language": None,
            "segment_count": 0,
            "text_length": 0,
            "timestamp_coverage": 0.0,
            "estimated_content_coverage": 0.0,
            "suspected_mismatch": False,
            "mismatch_checks": {},
            "error_class": None,
            "error_message": None,
            "retrieved_at": utc_now(),
            "normalized_path": None,
            "raw_path": None,
        }

    def write_raw(self, provider: str, video_id: str, value: Any, suffix: str = "json") -> str:
        directory = self.output / "raw" / provider
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{video_id}.{suffix}"
        if suffix.endswith("json"):
            path.write_text(json.dumps(sanitized(value, self.secrets), ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            path.write_text(clean_error(value, self.secrets) if suffix == "error.txt" else str(value), encoding="utf-8")
        return str(path.relative_to(self.output))

    def finish_success(
        self,
        record: dict[str, Any],
        meta: dict[str, Any],
        segments: list[dict[str, Any]],
        source_kind: str,
        language: str | None,
        returned_video_id: str | None,
        provider_name: str,
        audio: dict[str, Any] | None = None,
        identity_is_requested_url: bool = False,
        provider_response_id: str | None = None,
    ) -> dict[str, Any]:
        text = full_text(segments)
        quality, checks = quality_for(meta, segments, language, returned_video_id, identity_is_requested_url)
        record.update({
            "source_kind": source_kind,
            "language": language,
            "segment_count": len(segments),
            "text_length": len(text),
            "timestamp_coverage": quality["timestamp_coverage"],
            "estimated_content_coverage": quality["coverage"],
            "suspected_mismatch": quality["suspected_mismatch"],
            "mismatch_checks": checks,
        })
        if quality["suspected_mismatch"]:
            record.update({
                "status": "failed",
                "failure_taxonomy": "content_mismatch",
                "error_class": "content_mismatch",
                "error_message": "one or more hard mismatch checks failed",
            })
            return record
        record["status"] = "success" if quality["coverage"] >= 0.65 or len(text) >= 1000 else "partial"
        if record["status"] == "partial":
            record["failure_taxonomy"] = "partial"
        attempt = {
            "provider": record["provider"],
            "started_at": record.get("started_at"),
            "finished_at": record.get("finished_at"),
            "status": normalized_attempt_status(record),
            "http_status": record.get("http_status"),
            "latency_ms": record.get("latency_ms"),
            "cost_units": record.get("cost_units"),
            "error_code": record.get("failure_taxonomy"),
            "error_message": record.get("error_message"),
        }
        normalized = {
            "schema_version": "1.0",
            "content_id": meta["video_id"],
            "canonical_url": f"https://www.youtube.com/watch?v={meta['video_id']}",
            "status": record["status"],
            "provider": provider_name,
            "provider_version": record["provider"],
            "source_kind": source_kind,
            "language": language,
            "segments": segments,
            "full_text": text,
            "timestamp_coverage": quality["timestamp_coverage"],
            "retrieved_at": record["retrieved_at"],
            "audio": audio or {"used": False, "temporary": True, "provider": None, "asr_model": None},
            "quality": quality,
            "provenance": {
                "provider_response_id": provider_response_id,
                "notes": [f"{key}={value}" for key, value in checks.items()],
            },
            "attempts": [attempt],
        }
        relative = self.write_raw(record["provider"], meta["video_id"], normalized, "normalized.json")
        record["normalized_path"] = relative
        return record

    def finish_failure(
        self,
        record: dict[str, Any],
        message: Any,
        http_status: int | None = None,
        taxonomy: str | None = None,
    ) -> dict[str, Any]:
        clean = clean_error(message, self.secrets)
        record.update({
            "status": "failed",
            "failure_taxonomy": taxonomy or classify_failure(http_status, clean),
            "http_status": http_status,
            "error_class": taxonomy or classify_failure(http_status, clean),
            "error_message": clean,
        })
        return record

    def attempt_scrapecreators(self, record: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
        key = self.keys["scrapecreators"]
        assert key
        response = self.http.get(
            "https://api.scrapecreators.com/v1/youtube/video/transcript",
            headers={"x-api-key": key, "User-Agent": UA},
            params={"url": f"https://www.youtube.com/watch?v={meta['video_id']}"},
            timeout=90,
        )
        record["http_status"] = response.status_code
        try:
            data = response.json()
        except ValueError:
            data = {"body": response.text[:5000]}
        record["raw_path"] = self.write_raw(record["provider"], meta["video_id"], data)
        if response.status_code != 200:
            return self.finish_failure(record, data, response.status_code)
        transcript = data.get("transcript") or []
        record["cost_units"] = data.get("credits_charged")
        if not transcript:
            return self.finish_failure(record, "no transcript returned", response.status_code, "no_transcript")
        segments = []
        for item in transcript:
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            start = float(item.get("startMs") or 0) / 1000
            end = float(item.get("endMs") or item.get("startMs") or 0) / 1000
            segments.append({"start": start, "end": max(start, end), "text": text})
        if not segments:
            return self.finish_failure(record, "transcript payload was empty", response.status_code, "no_transcript")
        return self.finish_success(
            record, meta, segments, "provider_transcript", data.get("language"),
            data.get("videoId") or data.get("video_id"), "scrapecreators",
            identity_is_requested_url=(data.get("url") == f"https://www.youtube.com/watch?v={meta['video_id']}"),
            provider_response_id=data.get("requestId") or data.get("id"),
        )

    def firecrawl_request(self, url: str, formats: list[str]) -> requests.Response:
        key = self.keys["firecrawl"]
        assert key
        return self.http.post(
            "https://api.firecrawl.dev/v2/scrape",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": UA},
            json={"url": url, "formats": formats},
            timeout=180,
        )

    def attempt_firecrawl_transcript(self, record: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
        url = f"https://www.youtube.com/watch?v={meta['video_id']}"
        response = self.firecrawl_request(url, ["markdown"])
        record["http_status"] = response.status_code
        try:
            data = response.json()
        except ValueError:
            data = {"body": response.text[:5000]}
        record["raw_path"] = self.write_raw(record["provider"], meta["video_id"], data)
        if response.status_code not in (200, 201):
            return self.finish_failure(record, data, response.status_code)
        payload = data.get("data") or {}
        markdown = payload.get("markdown") or ""
        segments = extract_web_transcript(markdown)
        if not segments:
            return self.finish_failure(record, "page fetched but no transcript DOM was exposed", response.status_code, "no_transcript")
        metadata = payload.get("metadata") or {}
        source_url = metadata.get("sourceURL") or metadata.get("url")
        returned_id = meta["video_id"] if source_url and meta["video_id"] in source_url else None
        return self.finish_success(
            record, meta, segments, "web_transcript", None, returned_id, "firecrawl",
            identity_is_requested_url=(source_url == url), provider_response_id=data.get("id"),
        )

    def attempt_jina(self, record: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
        target = f"https://r.jina.ai/http://www.youtube.com/watch?v={meta['video_id']}"
        headers = {"User-Agent": UA, "Accept": "text/plain"}
        if self.keys["jina"]:
            headers["Authorization"] = f"Bearer {self.keys['jina']}"
        response = self.http.get(target, headers=headers, timeout=120)
        record["http_status"] = response.status_code
        record["raw_path"] = self.write_raw(record["provider"], meta["video_id"], response.text, "txt")
        if response.status_code != 200:
            return self.finish_failure(record, response.text[:2000], response.status_code)
        segments = extract_web_transcript(response.text)
        if not segments:
            return self.finish_failure(record, "reader returned page text without transcript DOM", response.status_code, "no_transcript")
        return self.finish_success(
            record, meta, segments, "web_transcript", None, meta["video_id"], "jina",
            identity_is_requested_url=True,
        )

    def attempt_youtube_transcript_api(self, record: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
        from youtube_transcript_api import YouTubeTranscriptApi

        try:
            fetched = YouTubeTranscriptApi().fetch(meta["video_id"], languages=LANGS)
        except Exception as exc:
            record["raw_path"] = self.write_raw(record["provider"], meta["video_id"], {"error": type(exc).__name__, "message": str(exc)})
            taxonomy = classify_failure(None, f"{type(exc).__name__}: {exc}")
            if type(exc).__name__ in {"NoTranscriptFound", "TranscriptsDisabled"}:
                taxonomy = "no_transcript"
            return self.finish_failure(record, f"{type(exc).__name__}: {exc}", taxonomy=taxonomy)
        segments = []
        for item in fetched:
            text = str(getattr(item, "text", "") or "").strip()
            if text:
                start = float(getattr(item, "start", 0) or 0)
                duration = float(getattr(item, "duration", 0) or 0)
                segments.append({"start": start, "end": start + duration, "text": text})
        record["raw_path"] = self.write_raw(record["provider"], meta["video_id"], {"language": getattr(fetched, "language_code", None), "segments": segments})
        if not segments:
            return self.finish_failure(record, "no transcript returned", taxonomy="no_transcript")
        return self.finish_success(
            record, meta, segments, "auto_caption", getattr(fetched, "language_code", None),
            meta["video_id"], "local", identity_is_requested_url=True,
        )

    def run_ytdlp(self, args: list[str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
        proxy_args = ["--proxy", self.proxy_url] if self.proxy_url else []
        return subprocess.run(
            [str(YTDLP), *YTDLP_COMMON, *proxy_args, *args], text=True, capture_output=True, timeout=timeout,
        )

    def attempt_ytdlp_caption(self, record: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
        url = f"https://www.youtube.com/watch?v={meta['video_id']}"
        with tempfile.TemporaryDirectory(prefix=f"sera-caption-{meta['video_id']}-") as tmp:
            output_template = str(Path(tmp) / "%(id)s.%(ext)s")
            result = self.run_ytdlp([
                "--skip-download", "--write-subs", "--write-auto-subs",
                "--sub-langs", ",".join(LANGS), "--sub-format", "vtt",
                "-o", output_template, url,
            ], timeout=240)
            files = sorted(Path(tmp).glob("*.vtt"), key=lambda path: ("zh" not in path.name.lower(), "en" in path.name.lower()))
            diagnostic = {"returncode": result.returncode, "stderr": result.stderr[-3000:], "files": [path.name for path in files]}
            record["raw_path"] = self.write_raw(record["provider"], meta["video_id"], diagnostic)
            if not files:
                taxonomy = classify_failure(None, result.stderr)
                if result.returncode == 0 or taxonomy == "provider_error":
                    taxonomy = "no_transcript"
                return self.finish_failure(record, result.stderr or "no caption files", taxonomy=taxonomy)
            chosen = files[0]
            segments = parse_vtt(chosen)
            if not segments:
                return self.finish_failure(record, "caption VTT parsed empty", taxonomy="no_transcript")
            lang_match = re.search(rf"{re.escape(meta['video_id'])}\.([^.]+)\.vtt$", chosen.name)
            language = lang_match.group(1) if lang_match else None
            source_kind = "auto_caption" if "auto" in chosen.name.lower() else "manual_caption"
            return self.finish_success(
                record, meta, segments, source_kind, language, meta["video_id"], "local",
                identity_is_requested_url=True,
            )

    def whisper_model(self) -> Any:
        if self.whisper is None:
            from faster_whisper import WhisperModel

            print(f"loading faster-whisper model={self.model_name}", flush=True)
            self.whisper = WhisperModel(
                self.model_name, device="cpu", compute_type="int8", cpu_threads=4, num_workers=1,
            )
        return self.whisper

    def transcribe(self, audio: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        stream, info = self.whisper_model().transcribe(
            str(audio), language="zh", beam_size=3, vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500}, condition_on_previous_text=True,
        )
        segments = [
            {"start": float(item.start), "end": float(item.end), "text": str(item.text or "").strip()}
            for item in stream if str(item.text or "").strip()
        ]
        return segments, {
            "language": getattr(info, "language", None),
            "language_probability": getattr(info, "language_probability", None),
            "duration": getattr(info, "duration", None),
            "duration_after_vad": getattr(info, "duration_after_vad", None),
        }

    def attempt_firecrawl_audio(self, record: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
        url = f"https://www.youtube.com/watch?v={meta['video_id']}"
        response = self.firecrawl_request(url, ["audio"])
        record["http_status"] = response.status_code
        try:
            data = response.json()
        except ValueError:
            data = {"body": response.text[:5000]}
        payload = data.get("data") or {}
        audio_url = payload.get("audio")
        persisted = json.loads(json.dumps(data))
        if isinstance(persisted.get("data"), dict) and persisted["data"].get("audio"):
            persisted["data"]["audio"] = "[redacted-signed-url]"
        record["raw_path"] = self.write_raw(record["provider"], meta["video_id"], persisted)
        if response.status_code not in (200, 201):
            return self.finish_failure(record, data, response.status_code)
        if not audio_url:
            return self.finish_failure(record, "Firecrawl returned no audio URL", response.status_code, "audio_unavailable")
        with tempfile.TemporaryDirectory(prefix=f"sera-firecrawl-audio-{meta['video_id']}-") as tmp:
            audio = Path(tmp) / f"{meta['video_id']}.audio"
            try:
                with self.http.get(audio_url, stream=True, timeout=180) as media:
                    media.raise_for_status()
                    with audio.open("wb") as handle:
                        for chunk in media.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                handle.write(chunk)
                if audio.stat().st_size < 10_000:
                    return self.finish_failure(record, "managed audio payload was too small", taxonomy="audio_unavailable")
                segments, info = self.transcribe(audio)
            finally:
                if audio.exists():
                    audio.unlink()
        if not segments:
            return self.finish_failure(record, "managed audio ASR produced no transcript", taxonomy="no_transcript")
        return self.finish_success(
            record, meta, segments, "provider_asr", info.get("language"), meta["video_id"], "firecrawl",
            audio={"used": True, "temporary": True, "provider": "firecrawl", "asr_model": f"faster-whisper-{self.model_name}"},
            identity_is_requested_url=True, provider_response_id=data.get("id"),
        )

    def download_local_audio(self, meta: dict[str, Any], work: Path) -> tuple[Path | None, dict[str, Any]]:
        url = f"https://www.youtube.com/watch?v={meta['video_id']}"
        output_template = str(work / f"{meta['video_id']}.%(ext)s")
        result = self.run_ytdlp([
            "--no-playlist", "--fragment-retries", "3", "--write-info-json",
            "-f", "bestaudio/best", "-o", output_template, url,
        ], timeout=300)
        candidates = [
            path for path in work.glob(f"{meta['video_id']}.*")
            if path.is_file() and path.suffix != ".json" and path.stat().st_size > 10_000
        ]
        info_path = work / f"{meta['video_id']}.info.json"
        info: dict[str, Any] = {}
        if info_path.exists():
            try:
                payload = json.loads(info_path.read_text(encoding="utf-8"))
                info = {"id": payload.get("id"), "title": payload.get("title"), "duration": payload.get("duration")}
            except ValueError:
                pass
        diagnostic = {"returncode": result.returncode, "stderr": result.stderr[-3000:], "metadata": info}
        if result.returncode == 0 and candidates:
            return max(candidates, key=lambda path: path.stat().st_size), diagnostic
        return None, diagnostic

    def attempt_local_audio_asr(self, record: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix=f"sera-local-audio-{meta['video_id']}-") as tmp:
            audio, diagnostic = self.download_local_audio(meta, Path(tmp))
            record["raw_path"] = self.write_raw(record["provider"], meta["video_id"], diagnostic)
            if not audio:
                taxonomy = classify_failure(None, diagnostic.get("stderr") or "")
                if taxonomy == "provider_error":
                    taxonomy = "audio_unavailable"
                return self.finish_failure(record, diagnostic.get("stderr") or "local audio unavailable", taxonomy=taxonomy)
            try:
                segments, info = self.transcribe(audio)
            finally:
                if audio.exists():
                    audio.unlink()
        if not segments:
            return self.finish_failure(record, "local ASR produced no transcript", taxonomy="no_transcript")
        returned_id = (diagnostic.get("metadata") or {}).get("id")
        return self.finish_success(
            record, meta, segments, "local_asr", info.get("language"), returned_id, "local",
            audio={"used": True, "temporary": True, "provider": "local", "asr_model": f"faster-whisper-{self.model_name}"},
            identity_is_requested_url=True,
        )

    def attempt(self, provider: str, meta: dict[str, Any]) -> dict[str, Any]:
        record = self.base_record(provider, meta)
        if not record["configured"]:
            return record
        handlers: dict[str, Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
            "scrapecreators": self.attempt_scrapecreators,
            "firecrawl_transcript": self.attempt_firecrawl_transcript,
            "jina": self.attempt_jina,
            "local_youtube_transcript_api": self.attempt_youtube_transcript_api,
            "local_ytdlp_caption": self.attempt_ytdlp_caption,
            "firecrawl_audio": self.attempt_firecrawl_audio,
            "local_audio_asr": self.attempt_local_audio_asr,
        }
        if provider in {"supadata", "apify"}:
            return self.finish_failure(record, "credential present but no benchmark adapter is configured", taxonomy="bad_request")
        started = time.monotonic()
        record.update({"attempted": True, "started_at": utc_now()})
        try:
            record = handlers[provider](record, meta)
        except requests.Timeout as exc:
            record = self.finish_failure(record, exc, taxonomy="timeout")
        except subprocess.TimeoutExpired as exc:
            record = self.finish_failure(record, exc, taxonomy="timeout")
        except Exception as exc:
            record = self.finish_failure(record, f"{type(exc).__name__}: {exc}")
        record["finished_at"] = utc_now()
        record["retrieved_at"] = record["finished_at"]
        record["latency_ms"] = round((time.monotonic() - started) * 1000, 1)
        return record

    def save_state(self) -> None:
        records = sorted(self.records.values(), key=lambda item: (VIDEO_IDS.index(item["video_id"]), PROVIDERS.index(item["provider"])))
        payload = {"schema_version": "1.0", "video_ids": VIDEO_IDS, "updated_at": utc_now(), "records": records}
        self.state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.write_outputs(records)

    def write_outputs(self, records: list[dict[str, Any]]) -> None:
        result_path = self.output / "acquisition-results.json"
        result_path.write_text(json.dumps({"video_ids": VIDEO_IDS, "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
        with (self.output / "acquisition-results.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=CSV_FIELDS, extrasaction="ignore", lineterminator="\n",
            )
            writer.writeheader()
            for record in records:
                row = dict(record)
                row["suspected_mismatch"] = str(row["suspected_mismatch"]).lower()
                writer.writerow(row)
        summaries = self.provider_summaries(records)
        recommendation = self.recommend(summaries)
        summary_payload = {
            "schema_version": "1.0",
            "sample_size": len(VIDEO_IDS),
            "expected_attempt_records": len(VIDEO_IDS) * len(PROVIDERS),
            "actual_attempt_records": len(records),
            "execution": {
                "host_type": "local_mac",
                "network_mode": "macos_system_proxy" if self.proxy_url else "direct",
                "proxy_endpoint_persisted": False,
                "asr_model": f"faster-whisper-{self.model_name}",
            },
            "providers": summaries,
            "recommendation": recommendation,
            "generated_at": utc_now(),
        }
        (self.output / "provider-summary.json").write_text(
            json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (self.output / "PROVIDER_BENCHMARK_REPORT.md").write_text(
            self.render_report(records, summaries, recommendation), encoding="utf-8"
        )

    def provider_summaries(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        summaries = []
        for provider in PROVIDERS:
            items = [item for item in records if item["provider"] == provider]
            attempted = [item for item in items if item["attempted"]]
            successes = [item for item in attempted if item["status"] == "success"]
            partials = [item for item in attempted if item["status"] == "partial"]
            failures = [item for item in attempted if item["status"] == "failed"]
            latencies = [float(item["latency_ms"]) for item in attempted if item.get("latency_ms") is not None]
            costs = [float(item["cost_units"]) for item in attempted if item.get("cost_units") is not None]
            summary = {
                "provider": provider,
                "label": PROVIDER_LABELS[provider],
                "configured_videos": sum(1 for item in items if item["configured"]),
                "attempted_videos": len(attempted),
                "successful_videos": len(successes),
                "partial_videos": len(partials),
                "failed_videos": len(failures),
                "not_configured_videos": sum(1 for item in items if item["status"] == "not_configured"),
                "success_rate": round(len(successes) / len(attempted), 4) if attempted else None,
                "content_mismatch_rate": round(sum(item["failure_taxonomy"] == "content_mismatch" for item in attempted) / len(attempted), 4) if attempted else None,
                "timestamp_full_rate": round(sum(item["timestamp_coverage"] >= 0.95 for item in successes) / len(successes), 4) if successes else None,
                "median_latency_ms": round(statistics.median(latencies), 1) if latencies else None,
                "mean_latency_ms": round(statistics.mean(latencies), 1) if latencies else None,
                "known_cost_units": round(sum(costs), 4) if costs else None,
                "native_transcript_count": sum(item["source_kind"] in {"manual_caption", "auto_caption", "provider_transcript", "web_transcript"} for item in successes),
                "asr_count": sum(item["source_kind"] in {"provider_asr", "local_asr"} for item in successes),
                "failure_taxonomy": dict(Counter(item["failure_taxonomy"] or "unknown" for item in failures)),
            }
            summaries.append(summary)
        return summaries

    def recommend(self, summaries: list[dict[str, Any]]) -> dict[str, Any]:
        by_id = {item["provider"]: item for item in summaries}
        transcript_ids = ["supadata", "scrapecreators", "apify", "firecrawl_transcript", "jina"]
        qualified = [
            by_id[provider] for provider in transcript_ids
            if by_id[provider]["successful_videos"] > 0 and by_id[provider]["content_mismatch_rate"] == 0
        ]
        qualified.sort(
            key=lambda item: (
                item["success_rate"] or 0,
                item["timestamp_full_rate"] or 0,
                -(item["median_latency_ms"] or float("inf")),
            ),
            reverse=True,
        )
        primary = qualified[0]["provider"] if qualified else None
        backup = qualified[1]["provider"] if len(qualified) > 1 else None
        managed = "firecrawl_audio" if by_id["firecrawl_audio"]["successful_videos"] else None
        local_candidates = [
            by_id[provider] for provider in
            ("local_youtube_transcript_api", "local_ytdlp_caption", "local_audio_asr")
            if by_id[provider]["successful_videos"] > 0 and by_id[provider]["content_mismatch_rate"] == 0
        ]
        local_candidates.sort(
            key=lambda item: (
                item["success_rate"] or 0,
                item["timestamp_full_rate"] or 0,
                -(item["median_latency_ms"] or float("inf")),
            ),
            reverse=True,
        )
        local = local_candidates[0]["provider"] if local_candidates else None
        return {
            "primary_transcript_provider": primary,
            "backup_transcript_provider": backup,
            "managed_audio_fallback": managed,
            "local_residential_fallback": local,
            "promotion_gate_passed": bool(primary and (backup or local)),
            "reason": (
                "Ranked by observed success rate, mismatch safety, timestamp quality, and latency."
                if primary else
                "No managed transcript provider succeeded; keep managed Primary/Backup unpromoted and use the observed local/residential fallback."
            ),
        }

    def render_report(
        self,
        records: list[dict[str, Any]],
        summaries: list[dict[str, Any]],
        recommendation: dict[str, Any],
    ) -> str:
        lines = [
            "# Sera Creator Intelligence Acquisition Benchmark",
            "",
            f"Generated: {utc_now()}",
            "",
            "Scope: acquisition only for the fixed 10-video sample. No intelligence analysis, scoring, Notion publishing, or backfill was run.",
            "",
            "## Provider Summary",
            "",
            "| Provider | Configured | Attempted | Success | Partial | Failed | Success rate | Timestamp-full | Median latency | Known units |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for item in summaries:
            success_rate = "n/a" if item["success_rate"] is None else f"{item['success_rate'] * 100:.1f}%"
            timestamp_rate = "n/a" if item["timestamp_full_rate"] is None else f"{item['timestamp_full_rate'] * 100:.1f}%"
            latency = "n/a" if item["median_latency_ms"] is None else f"{item['median_latency_ms']:.0f} ms"
            units = "n/a" if item["known_cost_units"] is None else str(item["known_cost_units"])
            lines.append(
                f"| {item['label']} | {item['configured_videos']} | {item['attempted_videos']} | "
                f"{item['successful_videos']} | {item['partial_videos']} | {item['failed_videos']} | "
                f"{success_rate} | {timestamp_rate} | {latency} | {units} |"
            )
        lines.extend(["", "## Per-video Matrix", ""])
        header = "| Video ID | " + " | ".join(PROVIDER_LABELS[provider] for provider in PROVIDERS) + " |"
        lines.extend([header, "|---|" + "---|" * len(PROVIDERS)])
        lookup = {(item["video_id"], item["provider"]): item for item in records}
        for video_id in VIDEO_IDS:
            cells = []
            for provider in PROVIDERS:
                item = lookup.get((video_id, provider))
                if not item:
                    cells.append("pending")
                elif item["status"] == "not_configured":
                    cells.append("NC")
                elif item["status"] == "success":
                    cells.append(f"S ({item['segment_count']})")
                elif item["status"] == "partial":
                    cells.append(f"P ({item['segment_count']})")
                else:
                    cells.append(f"F ({item['failure_taxonomy']})")
            lines.append(f"| `{video_id}` | " + " | ".join(cells) + " |")
        lines.extend(["", "Legend: S = success, P = partial, F = failed, NC = not configured; parentheses show segment count or failure taxonomy.", ""])
        lines.extend(["## Failure Taxonomy", ""])
        for item in summaries:
            if item["failure_taxonomy"]:
                rendered = ", ".join(f"{key}: {value}" for key, value in sorted(item["failure_taxonomy"].items()))
                lines.append(f"- {item['label']}: {rendered}")
        lines.extend([
            "",
            "## Recommendation",
            "",
            f"- Primary Transcript Provider: `{recommendation['primary_transcript_provider'] or 'none qualified'}`",
            f"- Backup Transcript Provider: `{recommendation['backup_transcript_provider'] or 'none qualified'}`",
            f"- Managed Audio Fallback: `{recommendation['managed_audio_fallback'] or 'none qualified'}`",
            f"- Local / Residential Fallback: `{recommendation['local_residential_fallback'] or 'none qualified'}`",
            f"- Promotion gate: `{'pass' if recommendation['promotion_gate_passed'] else 'fail'}`",
            "",
            recommendation["reason"],
            "",
            "## Validation Notes",
            "",
            f"- Fixed sample IDs: {len(VIDEO_IDS)}",
            f"- Attempt records: {len(records)} / {len(VIDEO_IDS) * len(PROVIDERS)}",
            f"- Suspected content mismatches: {sum(bool(item['suspected_mismatch']) for item in records)}",
            f"- Execution host: local Mac; network mode: {'macOS system proxy' if self.proxy_url else 'direct'}.",
            f"- ASR model: faster-whisper-{self.model_name}.",
            "- Every successful normalized transcript is stored beside its sanitized raw provider artifact.",
            "- Temporary audio and signed media URLs were deleted or redacted immediately after ASR.",
            "",
        ])
        return "\n".join(lines)

    def run(self) -> None:
        for provider in PROVIDERS:
            if provider not in self.selected:
                continue
            for index, video_id in enumerate(VIDEO_IDS, 1):
                key = f"{provider}::{video_id}"
                if key in self.records and not self.force:
                    print(f"[{provider} {index}/10] {video_id}: resume-skip", flush=True)
                    continue
                meta = self.catalog[video_id]
                record = self.attempt(provider, meta)
                self.records[key] = record
                self.save_state()
                print(
                    f"[{provider} {index}/10] {video_id}: {record['status']} "
                    f"taxonomy={record.get('failure_taxonomy')} segments={record['segment_count']} "
                    f"latency_ms={record.get('latency_ms')}",
                    flush=True,
                )
        self.save_state()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--env-file", type=Path, action="append", default=[],
        help="optional local env file; may be repeated and is never persisted",
    )
    parser.add_argument("--providers", help="comma-separated provider IDs; state is merged across runs")
    parser.add_argument("--model", default="small")
    parser.add_argument("--force", action="store_true", help="rerun selected provider attempts")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if VIDEO_IDS != list(dict.fromkeys(VIDEO_IDS)) or len(VIDEO_IDS) != 10:
        raise SystemExit("fixed sample must contain exactly 10 unique IDs")
    benchmark = Benchmark(args)
    try:
        benchmark.run()
    finally:
        benchmark.whisper = None


if __name__ == "__main__":
    main()
