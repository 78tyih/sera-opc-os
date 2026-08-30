#!/usr/bin/env python3
"""Lightweight stdlib validator for Sera Creator Intelligence bundles."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_VIDEO_TOP = {
    "schema_version", "video", "summary", "main_thesis", "claims",
    "scores", "watch_verdict", "provenance",
}
SCORE_LIMITS = {
    "insight": (0, 20),
    "evidence": (0, 15),
    "evergreen": (0, 20),
    "novelty": (0, 15),
    "argument_quality": (0, 15),
    "density": (0, 15),
    "knowledge_total": (0, 100),
    "personal_relevance": (0, 10),
}
VERDICTS = {"must_watch", "worth_watching", "skim", "note_only", "skip"}
CLAIM_TYPES = {"fact", "interpretation", "opinion", "prediction", "recommendation", "hypothesis"}


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_video(path: Path):
    errors = []
    try:
        data = load_json(path)
    except Exception as e:
        return [f"invalid JSON: {e}"]

    missing = REQUIRED_VIDEO_TOP - set(data)
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")
        return errors

    video = data.get("video") or {}
    if not video.get("video_id"):
        errors.append("video.video_id is required")
    if not video.get("title"):
        errors.append("video.title is required")
    if not video.get("url"):
        errors.append("video.url is required")
    if not str(data.get("main_thesis", "")).strip():
        errors.append("main_thesis is empty")

    scores = data.get("scores") or {}
    for key, (lo, hi) in SCORE_LIMITS.items():
        value = scores.get(key)
        if not isinstance(value, (int, float)) or not (lo <= value <= hi):
            errors.append(f"scores.{key} must be in [{lo}, {hi}]")

    verdict = data.get("watch_verdict") or {}
    if verdict.get("verdict") not in VERDICTS:
        errors.append("invalid watch_verdict.verdict")
    confidence = verdict.get("confidence")
    if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
        errors.append("watch_verdict.confidence must be in [0,1]")
    if not str(verdict.get("reason", "")).strip():
        errors.append("watch_verdict.reason is empty")

    for i, claim in enumerate(data.get("claims") or []):
        if claim.get("type") not in CLAIM_TYPES:
            errors.append(f"claims[{i}].type invalid")
        if not str(claim.get("text", "")).strip():
            errors.append(f"claims[{i}].text empty")
        if "evidence" not in claim:
            errors.append(f"claims[{i}].evidence missing")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", help="Creator Intelligence project root")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()

    required_dirs = ["catalog", "raw", "intelligence/videos", "state"]
    all_errors = []
    for rel in required_dirs:
        if not (root / rel).exists():
            all_errors.append(f"missing required path: {rel}")

    video_dir = root / "intelligence" / "videos"
    video_files = sorted(video_dir.glob("*.json")) if video_dir.exists() else []
    seen_ids = set()
    for path in video_files:
        errors = validate_video(path)
        if not errors:
            try:
                vid = load_json(path).get("video", {}).get("video_id")
                if vid in seen_ids:
                    errors.append(f"duplicate video_id: {vid}")
                elif vid:
                    seen_ids.add(vid)
            except Exception:
                pass
        for err in errors:
            all_errors.append(f"{path.name}: {err}")

    report_json = root / "reports" / "creator-intelligence.json"
    if report_json.exists():
        try:
            report = load_json(report_json)
            if "creator" not in report or "coverage" not in report:
                all_errors.append("creator report missing creator/coverage")
        except Exception as e:
            all_errors.append(f"creator report invalid JSON: {e}")

    print(f"root={root}")
    print(f"video_intelligence_files={len(video_files)}")
    print(f"unique_video_ids={len(seen_ids)}")
    if all_errors:
        print(f"status=FAIL errors={len(all_errors)}")
        for err in all_errors:
            print(f"- {err}")
        sys.exit(1)

    print("status=PASS")


if __name__ == "__main__":
    main()
