#!/usr/bin/env python3
"""Create a deterministic Living Design Benchmark snapshot from STYLE_DNA.json."""

from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path
from typing import Any

TRACKED_FIELDS = (
    "brand_personality",
    "color_system",
    "typography",
    "layout_language",
    "component_patterns",
    "design_patterns",
    "motion_language",
    "conversion_patterns",
)

def canonical_design_patterns(value: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(value, list):
        return out
    for item in value:
        if isinstance(item, str):
            out.append({"name": item})
        elif isinstance(item, dict) and isinstance(item.get("name"), str):
            out.append({k: copy.deepcopy(item[k]) for k in ("name", "category", "abstraction", "confidence") if k in item})
    return sorted(out, key=lambda x: x["name"].casefold())

def canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: canonicalize(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        if all(isinstance(x, str) for x in value):
            return sorted(set(value), key=str.casefold)
        return [canonicalize(x) for x in value]
    return value

def build_state(dna: dict[str, Any]) -> dict[str, Any]:
    state: dict[str, Any] = {}
    for key in TRACKED_FIELDS:
        if key not in dna:
            continue
        if key == "design_patterns":
            state[key] = canonical_design_patterns(dna[key])
        else:
            state[key] = canonicalize(copy.deepcopy(dna[key]))
    return state

def sha256_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Living Design Benchmark snapshot.")
    parser.add_argument("--target-id", required=True)
    parser.add_argument("--dna", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--freshness")
    args = parser.parse_args()

    dna_path = Path(args.dna).expanduser().resolve()
    dna = json.loads(dna_path.read_text(encoding="utf-8"))
    provenance = dna.get("provenance") if isinstance(dna.get("provenance"), dict) else {}
    state = build_state(dna)

    snapshot = {
        "schema_version": "1.0.0",
        "target_id": args.target_id,
        "source_url": provenance.get("source_url"),
        "captured_at": provenance.get("captured_at"),
        "freshness": args.freshness or provenance.get("freshness") or "unknown",
        "backend": provenance.get("extraction_backend"),
        "state": state,
        "coverage": sorted(state.keys()),
        "fingerprint": sha256_json(state),
        "evidence": {
            "dna_path": str(dna_path),
            "dna_sha256": file_sha256(dna_path),
        },
    }

    if args.manifest:
        manifest_path = Path(args.manifest).expanduser().resolve()
        snapshot["evidence"]["manifest_path"] = str(manifest_path)
        snapshot["evidence"]["manifest_sha256"] = file_sha256(manifest_path)

    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"target_id": args.target_id, "fingerprint": snapshot["fingerprint"]}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
