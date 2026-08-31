"""CLI for the Sera Learning OS runtime.

Examples:
  python -m core.sera_learning_os.cli --db memory/learning-os.db ingest signal.json
  python -m core.sera_learning_os.cli --db memory/learning-os.db maintain
  python -m core.sera_learning_os.cli --db memory/learning-os.db propose
  python -m core.sera_learning_os.cli --db memory/learning-os.db probe --proposal SEP.x --probe-id P1 --model codex --metric task_success_rate --baseline 0.7 --candidate 0.8
  python -m core.sera_learning_os.cli --db memory/learning-os.db assess-portability SEP.x
  python -m core.sera_learning_os.cli --db memory/learning-os.db review --out daily-learning.md
  python -m core.sera_learning_os.cli --db memory/learning-os.db export --context-hub ../SeraContextHub
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys

from .contradiction_export import export_contradictions_snapshot
from .daily_review import build_daily_review, render_daily_review_markdown
from .learning import init_learning_schema
from .pipeline import process_learning_signal
from .portability import assess_and_record_portability, assess_portability, record_portability_probe
from .skill_proposer import propose_ready_skills
from .wiki_export import export_context_hub_snapshot
from .wiki_maintainer import maintain_uncompiled_signals


def _connect(path: str) -> sqlite3.Connection:
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    init_learning_schema(conn)
    return conn


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise ValueError("learning signal JSON must be an object")
    return value


def cmd_ingest(conn: sqlite3.Connection, args) -> int:
    signal = _load_json(args.signal)
    result = process_learning_signal(conn, signal, auto_propose=not args.no_propose)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("error") else 0


def cmd_maintain(conn: sqlite3.Connection, args) -> int:
    result = maintain_uncompiled_signals(conn, limit=args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_propose(conn: sqlite3.Connection, args) -> int:
    result = propose_ready_skills(conn, limit=args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_probe(conn: sqlite3.Connection, args) -> int:
    result = record_portability_probe(
        conn,
        probe_id=args.probe_id,
        proposal_id=args.proposal,
        model=args.model,
        model_family=args.model_family,
        agent_shell=args.agent_shell,
        environment=args.environment,
        metric_name=args.metric,
        baseline_score=args.baseline,
        candidate_score=args.candidate,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("error") else 0


def cmd_assess_portability(conn: sqlite3.Connection, args) -> int:
    result = assess_portability(conn, args.proposal) if args.dry_run else assess_and_record_portability(conn, args.proposal)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("error") else 0


def cmd_review(conn: sqlite3.Connection, args) -> int:
    review = build_daily_review(conn, day=args.day)
    markdown = render_daily_review_markdown(review)
    if args.out:
        out_path = os.path.abspath(args.out)
        parent = os.path.dirname(out_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(markdown)
        print(out_path)
    else:
        print(markdown)
    return 0


def cmd_export(conn: sqlite3.Connection, args) -> int:
    wiki = export_context_hub_snapshot(conn, args.context_hub, day=args.day)
    contradictions = export_contradictions_snapshot(conn, args.context_hub)
    result = {
        **wiki,
        "contradiction_files_exported": contradictions["contradiction_files_exported"],
        "contradiction_files": contradictions["contradiction_files"],
        "git_commit_performed": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sera Learning OS")
    parser.add_argument("--db", default="memory/sera-learning.db", help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="process a Learning Signal through Raw/Wiki/Contradiction/Proposal")
    ingest.add_argument("signal", help="Learning Signal JSON file")
    ingest.add_argument("--no-propose", action="store_true", help="record learning but skip automatic proposal creation")
    ingest.set_defaults(func=cmd_ingest)

    maintain = sub.add_parser("maintain", help="compile raw signals not yet linked to a Wiki pattern")
    maintain.add_argument("--limit", type=int, default=500)
    maintain.set_defaults(func=cmd_maintain)

    propose = sub.add_parser("propose", help="create governed Skill proposals from verified patterns")
    propose.add_argument("--limit", type=int, default=200)
    propose.set_defaults(func=cmd_propose)

    probe = sub.add_parser("probe", help="append one baseline-vs-candidate portability probe")
    probe.add_argument("--proposal", required=True)
    probe.add_argument("--probe-id", required=True)
    probe.add_argument("--model", required=True)
    probe.add_argument("--model-family", default=None)
    probe.add_argument("--agent-shell", default=None)
    probe.add_argument("--environment", default=None)
    probe.add_argument("--metric", required=True)
    probe.add_argument("--baseline", required=True, type=float)
    probe.add_argument("--candidate", required=True, type=float)
    probe.set_defaults(func=cmd_probe)

    assess = sub.add_parser("assess-portability", help="evaluate cross-model negative transfer for a Skill proposal")
    assess.add_argument("proposal")
    assess.add_argument("--dry-run", action="store_true", help="calculate recommendation without recording Evaluation")
    assess.set_defaults(func=cmd_assess_portability)

    review = sub.add_parser("review", help="generate Daily Learning Review")
    review.add_argument("--day", default=None, help="UTC date YYYY-MM-DD; default today")
    review.add_argument("--out", default=None, help="optional Markdown output path")
    review.set_defaults(func=cmd_review)

    export = sub.add_parser("export", help="materialize Wiki snapshots into a SeraContextHub checkout")
    export.add_argument("--context-hub", required=True, help="path to local SeraContextHub checkout")
    export.add_argument("--day", default=None, help="UTC date YYYY-MM-DD; default today")
    export.set_defaults(func=cmd_export)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    conn = _connect(args.db)
    try:
        return args.func(conn, args)
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
