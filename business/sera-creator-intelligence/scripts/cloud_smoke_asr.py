#!/usr/bin/env python3
"""Ephemeral audio-download + ASR fallback for the 10-item Creator Intelligence smoke test.

Designed for GitHub Actions. Audio is downloaded to a temporary directory, transcribed,
and deleted immediately. Only transcript JSON is written to the output artifact.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

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

CLIENT_ATTEMPTS = [
    "mweb",
    "web_safari",
    "android_vr",
    "web_embedded",
    "tv",
]


def run(cmd: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)


def download_audio(video_id: str, work: Path) -> tuple[Path | None, str | None, list[str]]:
    url = f"https://www.youtube.com/watch?v={video_id}"
    errors: list[str] = []
    for client in CLIENT_ATTEMPTS:
        # clear previous failed attempt leftovers
        for p in work.glob(f"{video_id}.*"):
            try:
                p.unlink()
            except Exception:
                pass
        outtmpl = str(work / f"{video_id}.%(ext)s")
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--no-playlist",
            "--no-warnings",
            "--retries", "2",
            "--fragment-retries", "2",
            "--socket-timeout", "25",
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "--extractor-args", f"youtube:player_client={client}",
            "-f", "bestaudio/best",
            "-o", outtmpl,
            url,
        ]
        try:
            cp = run(cmd, timeout=180)
        except Exception as exc:
            errors.append(f"{client}:{type(exc).__name__}:{exc}")
            continue
        candidates = [p for p in work.glob(f"{video_id}.*") if p.is_file() and p.stat().st_size > 10_000]
        if cp.returncode == 0 and candidates:
            chosen = max(candidates, key=lambda p: p.stat().st_size)
            return chosen, client, errors
        err = (cp.stderr or cp.stdout or "download failed").replace("\n", " ").strip()[-1000:]
        errors.append(f"{client}:{err}")
    return None, None, errors


def transcribe(model: Any, audio: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    segments_iter, info = model.transcribe(
        str(audio),
        language="zh",
        beam_size=3,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        condition_on_previous_text=True,
    )
    segments = []
    for s in segments_iter:
        text = (s.text or "").strip()
        if text:
            segments.append({"start": float(s.start), "end": float(s.end), "text": text})
    info_obj = {
        "language": getattr(info, "language", None),
        "language_probability": getattr(info, "language_probability", None),
        "duration": getattr(info, "duration", None),
        "duration_after_vad": getattr(info, "duration_after_vad", None),
    }
    return segments, info_obj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default=os.environ.get("WHISPER_MODEL", "small"))
    args = ap.parse_args()

    out = Path(args.output).resolve()
    (out / "raw").mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="sera-henren-asr-"))

    from faster_whisper import WhisperModel  # type: ignore

    model = None
    results = []
    try:
        for idx, vid in enumerate(VIDEO_IDS, 1):
            print(f"[{idx}/{len(VIDEO_IDS)}] audio+ASR {vid}", flush=True)
            audio, client, download_errors = download_audio(vid, work)
            item: dict[str, Any] = {
                "video_id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "download_status": "success" if audio else "failed",
                "download_client": client,
                "download_errors": download_errors,
                "asr_status": "unavailable",
                "asr_model": args.model,
                "segments": [],
                "text": "",
            }
            if audio:
                try:
                    if model is None:
                        print(f"  loading faster-whisper model={args.model}", flush=True)
                        model = WhisperModel(args.model, device="cpu", compute_type="int8", cpu_threads=4, num_workers=1)
                    segs, info = transcribe(model, audio)
                    text = "\n".join(s["text"] for s in segs).strip()
                    item.update({
                        "asr_status": "available" if text else "empty",
                        "segments": segs,
                        "text": text,
                        "asr_info": info,
                    })
                    print(f"  client={client} audio_bytes={audio.stat().st_size} segments={len(segs)} chars={len(text)}", flush=True)
                except Exception as exc:
                    item["asr_status"] = "failed"
                    item["asr_error"] = f"{type(exc).__name__}:{exc}"
                    print(f"  ASR failed: {item['asr_error']}", flush=True)
                finally:
                    try:
                        audio.unlink()
                    except Exception:
                        pass
            else:
                print("  audio download failed on all clients", flush=True)

            (out / "raw" / f"{vid}.json").write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
            results.append(item)
            time.sleep(0.3)
    finally:
        # Runner temp disk is ephemeral, but explicitly remove any media remnants.
        for p in work.glob("*"):
            try:
                p.unlink()
            except Exception:
                pass
        try:
            work.rmdir()
        except Exception:
            pass

    summary = {
        "requested": len(VIDEO_IDS),
        "audio_downloaded": sum(1 for x in results if x["download_status"] == "success"),
        "asr_available": sum(1 for x in results if x["asr_status"] == "available"),
        "asr_failed_or_unavailable": sum(1 for x in results if x["asr_status"] != "available"),
        "model": args.model,
        "items": [
            {
                "video_id": x["video_id"],
                "download_status": x["download_status"],
                "download_client": x.get("download_client"),
                "asr_status": x["asr_status"],
                "segment_count": len(x.get("segments") or []),
                "char_count": len(x.get("text") or ""),
                "asr_info": x.get("asr_info"),
                "asr_error": x.get("asr_error"),
            }
            for x in results
        ],
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("requested", "audio_downloaded", "asr_available", "asr_failed_or_unavailable", "model")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
