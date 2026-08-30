#!/usr/bin/env python3
"""Import an existing Designlang output directory into the Sera evidence contract.

Use this for outputs produced elsewhere: MCP sessions, CI artifacts, another
agent, or a previous Designlang run. It never reruns extraction and never claims
capture capabilities that were not explicitly declared.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

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
    return path.suffix.lower().lstrip(".") or "unknown"


def iter_files(root: Path) -> Iterable[Path]:
    return (p for p in sorted(root.rglob("*")) if p.is_file())


def copy_tree(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for src in iter_files(source):
        rel = src.relative_to(source)
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register an existing Designlang output directory as Sera evidence."
    )
    parser.add_argument("--source-dir", required=True, help="Existing Designlang output directory")
    parser.add_argument("--url", required=True, help="Original website URL")
    parser.add_argument("--manifest", required=True, help="Output extraction-manifest.json")
    parser.add_argument("--copy-to-raw", help="Optional immutable raw destination; source is copied there first")
    parser.add_argument("--backend", default="designlang")
    parser.add_argument("--backend-version")
    parser.add_argument("--captured-at", help="Original extraction timestamp; defaults to import time")
    parser.add_argument("--source-repo")
    parser.add_argument("--source-commit")
    parser.add_argument("--source-path")
    parser.add_argument("--complete", action="store_true", help="Declare the imported artifact set complete")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--dark", action="store_true")
    parser.add_argument("--responsive", action="store_true")
    parser.add_argument("--interactions", action="store_true")
    parser.add_argument("--authenticated", action="store_true")
    args = parser.parse_args()

    source = Path(args.source_dir).expanduser().resolve()
    if not source.exists() or not source.is_dir():
        parser.error(f"--source-dir is not a directory: {source}")

    evidence_root = source
    imported_from = str(source)
    if args.copy_to_raw:
        raw = Path(args.copy_to_raw).expanduser().resolve()
        copy_tree(source, raw)
        evidence_root = raw

    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    artifacts = []
    for path in iter_files(evidence_root):
        artifacts.append({
            "path": str(path.relative_to(evidence_root)),
            "category": classify(path),
            "format": file_format(path),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "storage": "local",
        })

    captured_at = args.captured_at or datetime.now(timezone.utc).isoformat()
    notes = [
        "Imported existing extraction output; no website was crawled by this command.",
        "Capture flags below are declarations supplied by the importer and are not inferred.",
    ]
    if not args.complete:
        notes.append("Artifact completeness was not asserted; treat this import as partial evidence.")

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "url": args.url,
            "captured_at": captured_at,
            "backend": args.backend,
            "backend_version": args.backend_version,
        },
        "capture": {
            "full": args.full,
            "dark": args.dark,
            "responsive": args.responsive,
            "interactions": args.interactions,
            "screenshots": any(a["category"] == "screenshots" for a in artifacts),
            "authenticated": args.authenticated,
        },
        "artifacts": artifacts,
        "provenance": {
            "adapter": "extraction-engine/import_existing.py",
            "raw_output_dir": str(evidence_root),
            "imported_from": imported_from,
            "source_repo": args.source_repo,
            "source_commit": args.source_commit,
            "source_path": args.source_path,
            "import_mode": "existing_output",
        },
        "quality": {
            "complete": args.complete,
            "doctor_passed": False,
            "fallback_used": False,
            "exit_code": 0,
            "notes": notes,
        },
    }

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(artifacts)} artifacts → {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
