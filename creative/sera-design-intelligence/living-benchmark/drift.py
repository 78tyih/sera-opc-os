#!/usr/bin/env python3
"""Deterministic semantic drift classifier for Sera Design Intelligence V4.2."""

from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

POLICIES = {
    "brand_personality": {"weight": 4, "strategy": "set"},
    "color_system.primary": {"weight": 3, "strategy": "value"},
    "color_system.secondary": {"weight": 2, "strategy": "value"},
    "color_system.accent": {"weight": 1, "strategy": "value"},
    "color_system.background": {"weight": 2, "strategy": "value"},
    "typography.primary_font": {"weight": 4, "strategy": "value"},
    "typography.mono_font": {"weight": 3, "strategy": "value"},
    "typography.heading_style": {"weight": 4, "strategy": "object"},
    "typography.body_style": {"weight": 3, "strategy": "object"},
    "layout_language.grid": {"weight": 3, "strategy": "value"},
    "layout_language.section_style": {"weight": 3, "strategy": "value"},
    "component_patterns": {"weight": 4, "strategy": "set"},
    "design_patterns": {"weight": 5, "strategy": "pattern_set"},
    "motion_language": {"weight": 4, "strategy": "object"},
    "conversion_patterns": {"weight": 5, "strategy": "set"},
}
FORCE_MAJOR = {"design_patterns", "conversion_patterns"}

def get(data: dict[str, Any], dotted: str) -> Any:
    value: Any = data
    for part in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value

def pattern_names(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    out = set()
    for item in value:
        if isinstance(item, str):
            out.add(item.casefold())
        elif isinstance(item, dict) and isinstance(item.get("name"), str):
            out.add(item["name"].casefold())
    return out

def to_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(x).casefold() for x in value}

def compare_value(before: Any, after: Any, strategy: str) -> tuple[bool, dict[str, Any]]:
    if strategy == "set":
        b, a = to_set(before), to_set(after)
        return b != a, {"added": sorted(a-b), "removed": sorted(b-a)}
    if strategy == "pattern_set":
        b, a = pattern_names(before), pattern_names(after)
        return b != a, {"added": sorted(a-b), "removed": sorted(b-a)}
    return before != after, {"before": before, "after": after}

def classify(changes: list[dict[str, Any]], score: int) -> tuple[str, str, bool]:
    changed_fields = {c["field"] for c in changes}
    if not changes:
        return "none", "no_action", False
    if changed_fields & FORCE_MAJOR or score >= 10:
        return "major", "semantic_review_and_cross_site_recompute", True
    if score >= 5:
        return "moderate", "design_memory_review", True
    return "minor", "archive_snapshot_only", False

def build_report(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    if before.get("target_id") != after.get("target_id"):
        raise ValueError("Snapshots must belong to the same target_id")
    bstate = before.get("state") or {}
    astate = after.get("state") or {}
    changes = []
    score = 0
    for field, policy in POLICIES.items():
        b, a = get(bstate, field), get(astate, field)
        if b is None and a is None:
            continue
        # New measurement coverage is not design drift. Missing current
        # measurement is a data-quality issue and is also excluded from score.
        if b is None and a is not None:
            continue
        if b is not None and a is None:
            continue
        changed, delta = compare_value(b, a, policy["strategy"])
        if not changed:
            continue
        score += policy["weight"]
        changes.append({
            "field": field,
            "weight": policy["weight"],
            "strategy": policy["strategy"],
            "delta": delta,
        })
    severity, action, meaningful = classify(changes, score)
    return {
        "schema_version": "1.0.0",
        "target_id": before.get("target_id"),
        "source_url": after.get("source_url") or before.get("source_url"),
        "baseline": {"captured_at": before.get("captured_at"), "fingerprint": before.get("fingerprint"), "freshness": before.get("freshness")},
        "current": {"captured_at": after.get("captured_at"), "fingerprint": after.get("fingerprint"), "freshness": after.get("freshness")},
        "summary": {
            "change_count": len(changes),
            "meaningful_score": score,
            "severity": severity,
            "meaningful_change": meaningful,
            "memory_action": action,
        },
        "changes": changes,
        "policy_note": "Drift is evidence of change, not automatic evidence of improvement. Canonical memory updates require review.",
    }

def write_markdown(report: dict[str, Any], path: Path) -> None:
    s = report["summary"]
    lines = [
        f"# Design Drift · {report['target_id']}", "",
        f"- Severity: **{s['severity']}**",
        f"- Meaningful score: **{s['meaningful_score']}**",
        f"- Memory action: `{s['memory_action']}`",
        f"- Changes: {s['change_count']}", "",
        "| Weight | Field | Delta |", "|---:|---|---|",
    ]
    for change in report["changes"]:
        delta = json.dumps(change["delta"], ensure_ascii=False).replace("|", "\\|")
        lines.append(f"| {change['weight']} | `{change['field']}` | `{delta}` |")
    lines += ["", "> A changed design is not necessarily a better design. Review intent, product context and cross-site evidence before promotion.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two Living Design Benchmark snapshots.")
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    args = parser.parse_args()
    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after).read_text(encoding="utf-8"))
    report = build_report(before, after)
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
