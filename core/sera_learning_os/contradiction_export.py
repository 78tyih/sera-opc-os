"""Export append-only Pattern contradiction evidence into SeraContextHub."""

from __future__ import annotations

import os
import re
import sqlite3

from .contradictions import init_contradiction_schema, list_contradictions
from .learning import list_patterns


def _safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return value[:180] or "unnamed"


def render_contradictions_markdown(pattern_id: str, rows: list[dict]) -> str:
    lines = [
        f"# Pattern Contradictions — {pattern_id}",
        "",
        "> Append-only counter-evidence. Contradictions do not erase supporting evidence; they may move the materialized Pattern state to `contested`.",
        "",
    ]
    if not rows:
        lines.append("- No contradiction evidence.")
        return "\n".join(lines) + "\n"

    for item in rows:
        explicit = "explicit" if bool(item.get("explicit")) else "observed"
        lines.extend([
            f"## {item.get('evidence_ref')}",
            "",
            f"- at: `{item.get('at')}`",
            f"- source_agent: `{item.get('source_agent')}`",
            f"- source_model: `{item.get('source_model')}`",
            f"- task_context: `{item.get('task_context')}`",
            f"- strength: `{item.get('strength')}`",
            f"- mode: `{explicit}`",
            "",
            str(item.get("reason") or "—"),
            "",
        ])
    lines.extend([
        "## Governance",
        "",
        "- This file is counter-evidence, not a deletion request.",
        "- Production Skills are not modified by contradiction ingestion.",
        "- A contested Pattern may later be restored, superseded or narrowed after further evaluation; history remains retained.",
        "",
    ])
    return "\n".join(lines)


def export_contradictions_snapshot(conn: sqlite3.Connection, context_hub_root: str) -> dict:
    init_contradiction_schema(conn)
    root = os.path.abspath(context_hub_root)
    output_dir = os.path.join(root, "08_Wiki", "contradictions")
    os.makedirs(output_dir, exist_ok=True)

    exported = []
    for pattern in list_patterns(conn, limit=5000):
        pattern_id = pattern["pattern_id"]
        rows = list_contradictions(conn, pattern_id)
        if not rows:
            continue
        path = os.path.join(output_dir, _safe_name(pattern_id) + ".md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_contradictions_markdown(pattern_id, rows))
        exported.append(path)

    return {
        "contradiction_files_exported": len(exported),
        "contradiction_files": exported,
        "git_commit_performed": False,
    }
