#!/usr/bin/env python3
"""Sera Design Intelligence V4 — Designlang extraction adapter.

Runs designlang as the default URL extraction backend, preserves its raw output,
and emits a stable Sera `extraction-manifest.json` for upstream DNA/analysis
layers. The adapter intentionally does not interpret design quality.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

SCHEMA_VERSION = "1.0.0"
CATEGORY_RULES = (
    ("screenshots", ("screenshot", ".png", ".jpg", ".jpeg", ".webp")),
    ("agent_rules", ("agents.md", "agent", "cursorrule", "claude.md")),
    ("accessibility", ("a11y", "accessib", "wcag", "contrast")),
    ("responsive", ("responsive", "breakpoint", "viewport")),
    ("motion", ("motion", "keyframe", "transition", "animation")),
    ("typography", ("typography", "type.", "font")),
    ("components", ("component", "anatomy", "storybook")),
    ("tokens", ("token", "tailwind", "theme", "css-var", "variables")),
    ("brand", ("brand", "voice", "design.md")),
    ("platform", ("swift", "ios", "android", "compose", "flutter", "wordpress")),
    ("report", ("report", "grade", ".html", ".pdf")),
)


def run(cmd: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(path: Path) -> str:
    name = path.name.lower()
    rel = str(path).lower()
    for category, needles in CATEGORY_RULES:
        if any(needle in name or needle in rel for needle in needles):
            return category
    return "other"


def file_format(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    return suffix or "unknown"


def iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return (p for p in sorted(root.rglob("*")) if p.is_file())


def designlang_version() -> str | None:
    result = run(["npx", "-y", "designlang", "--version"])
    if result.returncode != 0:
        return None
    value = (result.stdout or result.stderr).strip().splitlines()
    return value[-1] if value else None


def build_manifest(*, url: str, raw_dir: Path, manifest_path: Path, command: list[str], doctor_passed: bool, exit_code: int | None, authenticated: bool, complete: bool, notes: list[str]) -> dict:
    artifacts = []
    for path in iter_files(raw_dir):
        try:
            artifact_path = path.relative_to(manifest_path.parent.parent)
        except ValueError:
            artifact_path = path
        artifacts.append({
            "path": str(artifact_path),
            "category": classify(path),
            "format": file_format(path),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "url": url,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "backend": "designlang",
            "backend_version": designlang_version(),
        },
        "capture": {
            "full": True,
            "dark": True,
            "responsive": True,
            "interactions": True,
            "screenshots": True,
            "authenticated": authenticated,
        },
        "artifacts": artifacts,
        "provenance": {
            "adapter": "extraction-engine/adapter.py",
            "raw_output_dir": str(raw_dir),
            "command": command,
            "doctor_command": ["npx", "-y", "designlang", "doctor"],
        },
        "quality": {
            "complete": complete,
            "doctor_passed": doctor_passed,
            "fallback_used": False,
            "exit_code": exit_code,
            "notes": notes,
        },
    }


def default_manifest_path(raw_dir: Path) -> Path:
    if raw_dir.name == "designlang" and raw_dir.parent.name == "raw":
        return raw_dir.parent.parent / "normalized" / "extraction-manifest.json"
    return raw_dir.parent / "normalized" / "extraction-manifest.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Designlang and emit a Sera extraction manifest.")
    parser.add_argument("url", help="Website URL to extract")
    parser.add_argument("--out", required=True, help="Raw Designlang output directory")
    parser.add_argument("--manifest", help="Override manifest output path")
    parser.add_argument("--cookie-file", help="Runtime-only cookie/storage-state file; contents are never persisted")
    parser.add_argument("--wait", type=int, default=0, help="Extra SPA wait in ms")
    parser.add_argument("--skip-doctor", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    args = parser.parse_args()

    parsed = urlparse(args.url if "://" in args.url else f"https://{args.url}")
    if not parsed.hostname:
        parser.error("A valid URL/hostname is required")

    raw_dir = Path(args.out).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve() if args.manifest else default_manifest_path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    if shutil.which("npx") is None:
        print("ERROR: npx is required. Install Node.js before running this adapter.", file=sys.stderr)
        return 127

    doctor_cmd = ["npx", "-y", "designlang", "doctor"]
    doctor_passed = True
    notes: list[str] = []
    if not args.skip_doctor:
        if args.dry_run:
            print("DRY RUN:", " ".join(doctor_cmd))
        else:
            doctor = run(doctor_cmd)
            doctor_passed = doctor.returncode == 0
            if not doctor_passed:
                notes.append("designlang doctor failed; extraction was not trusted as complete.")

    cmd = ["npx", "-y", "designlang", args.url, "--out", str(raw_dir), "--full", "--dark", "--emit-agent-rules"]
    if args.wait > 0:
        cmd += ["--wait", str(args.wait)]
    if args.cookie_file:
        cmd += ["--cookie-file", str(Path(args.cookie_file).expanduser())]

    if args.dry_run:
        print("DRY RUN:", " ".join(cmd))
        return 0

    if not doctor_passed:
        manifest = build_manifest(url=args.url, raw_dir=raw_dir, manifest_path=manifest_path, command=cmd, doctor_passed=False, exit_code=None, authenticated=bool(args.cookie_file), complete=False, notes=notes)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Manifest written with failed preflight: {manifest_path}", file=sys.stderr)
        return 2

    result = run(cmd)
    complete = result.returncode == 0
    if not complete:
        notes.append("designlang extraction failed; use sera-browser-automation fallback and preserve this manifest.")

    manifest = build_manifest(url=args.url, raw_dir=raw_dir, manifest_path=manifest_path, command=cmd, doctor_passed=doctor_passed, exit_code=result.returncode, authenticated=bool(args.cookie_file), complete=complete, notes=notes)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    print(f"Sera extraction manifest: {manifest_path}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
