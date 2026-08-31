#!/usr/bin/env python3
"""Fetch metadata + captions for the Creator Intelligence 10-item smoke test.

This script is designed for an ephemeral CI runner. It never commits transcripts;
all raw text is written only to the requested output directory so it can be
uploaded as a short-lived workflow artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

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
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36"
TRANSCRIPT_ENDPOINT = "https://youtubetranscript.com/?server_vid2={}"


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return html.unescape(str(value)).strip()


def sha256_text(text: str) -> str | None:
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_vtt(path: Path) -> list[dict[str, Any]]:
    """Very small VTT parser sufficient for YouTube caption output."""
    segments: list[dict[str, Any]] = []
    time_re = re.compile(r"(?:(\d+):)?(\d{2}):(\d{2}\.\d{3}) --> (?:(\d+):)?(\d{2}):(\d{2}\.\d{3})")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    i = 0
    seen: set[tuple[float, str]] = set()
    while i < len(lines):
        m = time_re.search(lines[i])
        if not m:
            i += 1
            continue
        sh, sm, ss, eh, em, es = m.groups()
        start = (int(sh or 0) * 3600) + int(sm) * 60 + float(ss)
        end = (int(eh or 0) * 3600) + int(em) * 60 + float(es)
        i += 1
        buff = []
        while i < len(lines) and lines[i].strip():
            text = re.sub(r"<[^>]+>", "", lines[i]).strip()
            if text and not text.startswith("Kind:") and not text.startswith("Language:"):
                buff.append(text)
            i += 1
        text = " ".join(buff)
        text = re.sub(r"\s+", " ", text).strip()
        key = (round(start, 3), text)
        if text and key not in seen:
            seen.add(key)
            segments.append({"text": text, "start": start, "duration": max(0.0, end - start)})
    return segments


def fetch_metadata(video_id: str) -> tuple[dict[str, Any], list[str]]:
    url = f"https://www.youtube.com/watch?v={video_id}"
    errors: list[str] = []
    meta: dict[str, Any] = {
        "video_id": video_id,
        "url": url,
        "title": None,
        "creator": "一个狠人",
        "channel_id": "UCJAPsTtcJJWGk8e-_CJL8TQ",
        "published_at": None,
        "duration_seconds": None,
        "view_count": None,
        "description": None,
    }

    try:
        r = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": url, "format": "json"},
            headers={"User-Agent": UA},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        meta["title"] = data.get("title")
        meta["creator"] = data.get("author_name") or meta["creator"]
    except Exception as exc:
        errors.append(f"oembed:{type(exc).__name__}:{exc}")

    try:
        cp = subprocess.run(
            [
                sys.executable, "-m", "yt_dlp",
                "--dump-single-json", "--skip-download", "--ignore-no-formats-error",
                "--no-warnings", url,
            ],
            text=True,
            capture_output=True,
            timeout=90,
        )
        if cp.returncode == 0 and cp.stdout.strip():
            data = json.loads(cp.stdout)
            meta.update({
                "title": data.get("title") or meta.get("title"),
                "creator": data.get("uploader") or data.get("channel") or meta.get("creator"),
                "channel_id": data.get("channel_id") or meta.get("channel_id"),
                "published_at": data.get("upload_date") or data.get("release_date"),
                "duration_seconds": data.get("duration"),
                "view_count": data.get("view_count"),
                "description": data.get("description"),
                "availability": data.get("availability"),
                "live_status": data.get("live_status"),
            })
        else:
            err = (cp.stderr or "yt-dlp metadata failed").strip().replace("\n", " ")[:500]
            errors.append(f"yt_dlp_metadata:{err}")
    except Exception as exc:
        errors.append(f"yt_dlp_metadata:{type(exc).__name__}:{exc}")
    return meta, errors


def transcript_via_public_endpoint(video_id: str) -> tuple[list[dict[str, Any]], str | None, str | None]:
    try:
        r = requests.get(
            TRANSCRIPT_ENDPOINT.format(video_id),
            headers={"User-Agent": UA, "Accept": "application/xml,text/xml,*/*"},
            timeout=30,
        )
        if r.status_code != 200:
            return [], None, f"http_{r.status_code}"
        if "YouTube is currently blocking us" in r.text:
            return [], None, "service_blocked"
        root = ET.fromstring(r.content)
        segments = []
        for node in root.findall(".//text"):
            text = safe_text("".join(node.itertext()))
            if not text:
                continue
            segments.append({
                "text": text,
                "start": float(node.attrib.get("start", 0) or 0),
                "duration": float(node.attrib.get("dur", 0) or 0),
            })
        return segments, "web_fallback", None if segments else "empty_xml"
    except Exception as exc:
        return [], None, f"{type(exc).__name__}:{exc}"


def transcript_via_api(video_id: str) -> tuple[list[dict[str, Any]], str | None, str | None, str | None]:
    langs = ["zh-CN", "zh-Hans", "zh-Hant", "zh", "en"]
    try:
        from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=langs)
        segments = []
        language = getattr(fetched, "language_code", None)
        for s in fetched:
            text = safe_text(getattr(s, "text", None) if hasattr(s, "text") else s.get("text"))
            start = getattr(s, "start", None) if hasattr(s, "start") else s.get("start", 0)
            dur = getattr(s, "duration", None) if hasattr(s, "duration") else s.get("duration", 0)
            if text:
                segments.append({"text": text, "start": float(start or 0), "duration": float(dur or 0)})
        return segments, "youtube_caption", language, None if segments else "empty_api"
    except Exception as first_exc:
        try:
            # Backward compatibility with older youtube-transcript-api releases.
            from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
            rows = YouTubeTranscriptApi.get_transcript(video_id, languages=langs)  # type: ignore[attr-defined]
            segments = [
                {"text": safe_text(x.get("text")), "start": float(x.get("start", 0)), "duration": float(x.get("duration", 0))}
                for x in rows if safe_text(x.get("text"))
            ]
            return segments, "youtube_caption", None, None if segments else "empty_api_old"
        except Exception as exc:
            return [], None, None, f"new={type(first_exc).__name__}:{first_exc};old={type(exc).__name__}:{exc}"


def transcript_via_ytdlp(video_id: str) -> tuple[list[dict[str, Any]], str | None, str | None, str | None]:
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with tempfile.TemporaryDirectory() as td:
            out = str(Path(td) / "%(id)s.%(ext)s")
            cp = subprocess.run(
                [
                    sys.executable, "-m", "yt_dlp", "--skip-download", "--ignore-no-formats-error",
                    "--write-subs", "--write-auto-subs", "--sub-langs", "zh-CN,zh-Hans,zh-Hant,zh,en",
                    "--sub-format", "vtt", "--no-warnings", "-o", out, url,
                ],
                text=True,
                capture_output=True,
                timeout=120,
            )
            files = sorted(Path(td).glob("*.vtt"))
            if not files:
                err = (cp.stderr or "no caption files").strip().replace("\n", " ")[:600]
                return [], None, None, err
            preferred = sorted(files, key=lambda p: ("zh" not in p.name.lower(), "en" in p.name.lower(), len(p.name)))
            chosen = preferred[0]
            segments = parse_vtt(chosen)
            lang = None
            m = re.search(r"\.([a-zA-Z-]+)\.vtt$", chosen.name)
            if m:
                lang = m.group(1)
            return segments, "auto_caption", lang, None if segments else "empty_vtt"
    except Exception as exc:
        return [], None, None, f"{type(exc).__name__}:{exc}"


def fetch_one(video_id: str) -> dict[str, Any]:
    metadata, metadata_errors = fetch_metadata(video_id)
    transcript_errors: list[str] = []

    segments, source, err = transcript_via_public_endpoint(video_id)
    language = None
    if err:
        transcript_errors.append(f"public_endpoint:{err}")

    if not segments:
        segments, source, language, err = transcript_via_api(video_id)
        if err:
            transcript_errors.append(f"youtube_transcript_api:{err}")

    if not segments:
        segments, source, language, err = transcript_via_ytdlp(video_id)
        if err:
            transcript_errors.append(f"yt_dlp_subtitles:{err}")

    text = "\n".join(s["text"] for s in segments).strip()
    return {
        **metadata,
        "transcript_status": "available" if text else "unavailable",
        "transcript_source": source,
        "language": language,
        "segment_count": len(segments),
        "segments": segments,
        "text": text,
        "transcript_sha256": sha256_text(text),
        "metadata_errors": metadata_errors,
        "transcript_errors": transcript_errors,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    out = Path(args.output).resolve()
    (out / "raw").mkdir(parents=True, exist_ok=True)

    results = []
    for idx, vid in enumerate(VIDEO_IDS, 1):
        print(f"[{idx}/{len(VIDEO_IDS)}] fetch {vid}", flush=True)
        item = fetch_one(vid)
        results.append(item)
        (out / "raw" / f"{vid}.json").write_text(
            json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # Do not print transcript text in CI logs.
        print(
            f"  title={item.get('title')!r} transcript={item['transcript_status']} "
            f"source={item.get('transcript_source')} segments={item['segment_count']}",
            flush=True,
        )
        time.sleep(0.5)

    summary = {
        "requested": len(VIDEO_IDS),
        "available_transcripts": sum(1 for x in results if x["transcript_status"] == "available"),
        "unavailable_transcripts": sum(1 for x in results if x["transcript_status"] != "available"),
        "sources": {},
        "items": [
            {
                "video_id": x["video_id"],
                "title": x.get("title"),
                "published_at": x.get("published_at"),
                "duration_seconds": x.get("duration_seconds"),
                "view_count": x.get("view_count"),
                "transcript_status": x.get("transcript_status"),
                "transcript_source": x.get("transcript_source"),
                "segment_count": x.get("segment_count"),
                "errors": x.get("transcript_errors"),
            }
            for x in results
        ],
    }
    for x in results:
        key = x.get("transcript_source") or "unavailable"
        summary["sources"][key] = summary["sources"].get(key, 0) + 1
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("requested", "available_transcripts", "unavailable_transcripts", "sources")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
