from __future__ import annotations

import argparse
import json

from sqlalchemy.orm import Session

from sera_message_intelligence.context_graph.self_actions import apply_self_signal_decision
from sera_message_intelligence.context_graph.store import list_graph_objects
from sera_message_intelligence.db import get_engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List or explicitly confirm/reject/supersede durable SelfSignals"
    )
    parser.add_argument(
        "--action",
        choices=["list", "confirm", "reject", "supersede"],
        default="list",
    )
    parser.add_argument("--id", help="Durable SelfSignal object ID")
    parser.add_argument(
        "--reference",
        help="Explicit user-decision reference. Required for confirm/reject/supersede.",
    )
    parser.add_argument("--note", help="Optional user note stored with the decision")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.action == "list":
        with Session(get_engine()) as session:
            records = list_graph_objects(session, "self_signal")
        rows = []
        for record in records:
            payload = record.payload
            rows.append(
                {
                    "id": record.object_id,
                    "statement": payload.get("statement"),
                    "signal_type": payload.get("signal_type"),
                    "status": payload.get("status"),
                    "evidence_level": payload.get("evidence_level"),
                    "confidence": payload.get("confidence"),
                    "window_start": payload.get("window_start"),
                    "window_end": payload.get("window_end"),
                    "source_diversity": payload.get("source_diversity"),
                }
            )
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    if not args.id:
        raise SystemExit("--id is required for confirm/reject/supersede")
    if not args.reference:
        raise SystemExit("--reference is required for confirm/reject/supersede")

    with Session(get_engine()) as session:
        result = apply_self_signal_decision(
            session,
            object_id=args.id,
            action=args.action,
            decision_reference=args.reference,
            note=args.note,
        )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
