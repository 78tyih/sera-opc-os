from __future__ import annotations

import argparse
from pathlib import Path

from sqlalchemy.orm import Session

from sera_message_intelligence.context_graph.radar import (
    build_context_radar,
    render_context_radar_markdown,
)
from sera_message_intelligence.context_graph.store import list_graph_objects
from sera_message_intelligence.db import get_engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Opportunity Radar and Commitment Tracker from durable context graph objects"
    )
    parser.add_argument("--output-root", default="reports/context-radar")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Session(get_engine()) as session:
        opportunities = list_graph_objects(session, "opportunity")
        commitments = list_graph_objects(session, "commitment")

    radar = build_context_radar(
        opportunity_records=opportunities,
        commitment_records=commitments,
    )
    root = Path(args.output_root)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "radar.json"
    markdown_path = root / "radar.md"
    json_path.write_text(radar.model_dump_json(indent=2), encoding="utf-8")
    markdown_path.write_text(render_context_radar_markdown(radar), encoding="utf-8")

    print(
        radar.model_dump_json(
            include={"generated_at", "opportunities", "commitments"},
            indent=None,
        )
    )
    print(f"json={json_path}")
    print(f"markdown={markdown_path}")


if __name__ == "__main__":
    main()
