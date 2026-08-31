"""CLI for the Sera Learning OS runtime.

Examples:
  python -m core.sera_learning_os.cli --db memory/learning-os.db ingest signal.json
  python -m core.sera_learning_os.cli --db memory/learning-os.db maintain
  python -m core.sera_learning_os.cli --db memory/learning-os.db propose
  python -m core.sera_learning_os.cli --db memory/learning-os.db review --out daily-learning.md
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys

from .daily_review import build_daily_review, render_daily_review_markdown
from .learning import init_learning_schema
from .skill_proposer import propose_ready_skills
from .wiki_maintainer import compile_signal_to_wiki, maintain_uncompiled_signals


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
    result = compile_signal_to_wiki(conn, signal)
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


def cmd_review(conn: sqlite3.Connection, args) -> int:
    review = build_daily_review(conn, day=args.day)
    markdown = render_daily_review_markdown(review)
    if args.out:
        out_path = os.path.abspath(args.out)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(markdown)
        print(out_path)
    else:
        print(markdown)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sera Learning OS")
    parser.add_argument("--db", default="memory/sera-learning.db", help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="record a Learning Signal and compile it to Wiki")
    ingest.add_argument("signal", help="Learning Signal JSON file")
    ingest.set_defaults(func=cmd_ingest)

    maintain = sub.add_parser("maintain", help="compile raw signals not yet linked to a Wiki pattern")
    maintain.add_argument("--limit", type=int, default=500)
    maintain.set_defaults(func=cmd_maintain)

    propose = sub.add_parser("propose", help="create governed Skill proposals from verified patterns")
    propose.add_argument("--limit", type=int, default=200)
    propose.set_defaults(func=cmd_propose)

    review = sub.add_parser("review", help="generate Daily Learning Review")
    review.add_argument("--day", default=None, help="UTC date YYYY-MM-DD; default today")
    review.add_argument("--out", default=None, help="optional Markdown output path")
    review.set_defaults(func=cmd_review)
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
