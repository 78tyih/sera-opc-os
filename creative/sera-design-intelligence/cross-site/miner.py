#!/usr/bin/env python3
"""Cross-site Pattern Miner for Sera Design Intelligence V4.1.

Consumes case-local STYLE_DNA.json files and produces a deterministic comparison
report. It only promotes semantic patterns repeated across independent sites.
No network access and no LLM inference are performed here.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

FIELDS = {
    "brand_personality": ("brand", "brand_personality"),
    "component_patterns": ("component", "component_patterns"),
    "conversion_patterns": ("conversion", "conversion_patterns"),
    "recommended_usage": ("usage", "recommended_usage"),
    "layout.section_style": ("layout", "layout_language.section_style"),
    "layout.grid": ("layout", "layout_language.grid"),
    "motion.hover_effect": ("motion", "motion_language.hover_effect"),
}


@dataclass
class Case:
    case_id: str
    root: Path
    dna: dict[str, Any]
    source_url: str | None
    domain: str


def nested_get(data: dict[str, Any], dotted: str) -> Any:
    value: Any = data
    for part in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def normalize_text(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[–—]", "-", value)
    return value


def to_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                label = item.get("pattern") or item.get("name") or item.get("type")
                if isinstance(label, str):
                    out.append(label)
        return out
    return []


def load_case(spec: str) -> Case:
    if "=" not in spec:
        raise ValueError("--case must use id=path")
    case_id, raw_path = spec.split("=", 1)
    root = Path(raw_path).expanduser().resolve()
    dna_path = root / "dna" / "STYLE_DNA.json"
    if not dna_path.exists():
        raise FileNotFoundError(f"{case_id}: missing {dna_path}")
    dna = json.loads(dna_path.read_text(encoding="utf-8"))
    provenance = dna.get("provenance") if isinstance(dna.get("provenance"), dict) else {}
    source_url = provenance.get("source_url")
    parsed = urlparse(source_url) if isinstance(source_url, str) else None
    domain = parsed.hostname.lower() if parsed and parsed.hostname else case_id
    return Case(case_id=case_id, root=root, dna=dna, source_url=source_url, domain=domain)


def collect_patterns(cases: list[Case]) -> dict[tuple[str, str], dict[str, Any]]:
    bucket: dict[tuple[str, str], dict[str, Any]] = {}
    for case in cases:
        for field_name, (pattern_type, dotted) in FIELDS.items():
            for raw_value in to_values(nested_get(case.dna, dotted)):
                normalized = normalize_text(raw_value)
                if not normalized:
                    continue
                key = (pattern_type, normalized)
                record = bucket.setdefault(key, {
                    "pattern_type": pattern_type,
                    "pattern": raw_value.strip(),
                    "normalized_pattern": normalized,
                    "fields": set(),
                    "sites": {},
                })
                record["fields"].add(field_name)
                record["sites"][case.case_id] = {
                    "domain": case.domain,
                    "source_url": case.source_url,
                    "evidence_ref": f"{case.case_id}:dna/{dotted}",
                }
    return bucket


def candidate_from_record(record: dict[str, Any], minimum_sites: int) -> dict[str, Any]:
    independent_domains = sorted({v["domain"] for v in record["sites"].values()})
    support_count = len(independent_domains)
    if support_count >= max(3, minimum_sites + 1):
        status = "strong_candidate"
        confidence = min(0.95, 0.62 + 0.08 * support_count)
    elif support_count >= minimum_sites:
        status = "candidate"
        confidence = min(0.85, 0.55 + 0.08 * support_count)
    else:
        status = "case_local"
        confidence = 0.40

    return {
        "pattern_type": record["pattern_type"],
        "pattern": record["pattern"],
        "normalized_pattern": record["normalized_pattern"],
        "support_count": support_count,
        "support_sites": sorted(record["sites"].keys()),
        "support_domains": independent_domains,
        "fields": sorted(record["fields"]),
        "evidence_refs": [record["sites"][k]["evidence_ref"] for k in sorted(record["sites"])],
        "confidence": round(confidence, 2),
        "status": status,
        "requires_human_review": status != "case_local",
    }


def build_report(cases: list[Case], minimum_sites: int) -> dict[str, Any]:
    records = collect_patterns(cases)
    candidates = [candidate_from_record(r, minimum_sites) for r in records.values()]
    candidates.sort(key=lambda x: (-x["support_count"], x["pattern_type"], x["normalized_pattern"]))

    return {
        "schema_version": "1.0.0",
        "study": {
            "case_count": len(cases),
            "independent_domain_count": len({c.domain for c in cases}),
            "minimum_independent_sites": minimum_sites,
            "cases": [
                {"id": c.case_id, "source_url": c.source_url, "domain": c.domain, "path": str(c.root)}
                for c in cases
            ],
        },
        "summary": {
            "strong_candidates": sum(c["status"] == "strong_candidate" for c in candidates),
            "candidates": sum(c["status"] == "candidate" for c in candidates),
            "case_local": sum(c["status"] == "case_local" for c in candidates),
        },
        "patterns": candidates,
        "promotion_note": "Candidates are not canonical memory until Design Review approves them.",
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Cross-site Pattern Mining Result",
        "",
        f"- Cases: {report['study']['case_count']}",
        f"- Independent domains: {report['study']['independent_domain_count']}",
        f"- Minimum support: {report['study']['minimum_independent_sites']}",
        "",
        "## Promotion Candidates",
        "",
        "| Status | Type | Pattern | Support | Confidence |",
        "|---|---|---|---:|---:|",
    ]
    promoted = [p for p in report["patterns"] if p["status"] != "case_local"]
    if not promoted:
        lines.append("| — | — | No cross-site candidates yet | 0 | — |")
    else:
        for p in promoted:
            pattern = p["pattern"].replace("|", "\\|")
            lines.append(f"| {p['status']} | {p['pattern_type']} | {pattern} | {p['support_count']} | {p['confidence']:.2f} |")
    lines += [
        "",
        "> Deterministic overlap only. Design Strategy / Review must decide whether the overlap is meaningful and reusable.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Mine repeated semantic design patterns across Sera case studies.")
    parser.add_argument("--case", action="append", required=True, help="Case in id=/path/to/case format; repeat at least twice")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument("--markdown", help="Optional Markdown summary path")
    parser.add_argument("--minimum-sites", type=int, default=2)
    args = parser.parse_args()

    if len(args.case) < 2:
        parser.error("At least two --case inputs are required")
    if args.minimum_sites < 2:
        parser.error("--minimum-sites must be >= 2")

    cases = [load_case(spec) for spec in args.case]
    if len({c.domain for c in cases}) < 2:
        parser.error("Cross-site mining requires at least two independent domains")

    report = build_report(cases, args.minimum_sites)
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.markdown:
        md = Path(args.markdown).expanduser().resolve()
        md.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(report, md)

    print(json.dumps(report["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
