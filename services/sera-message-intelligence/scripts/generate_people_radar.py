from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy.orm import Session

from sera_message_intelligence.context_graph.people_radar import (
    build_people_relationship_radar,
    render_people_radar_markdown,
)
from sera_message_intelligence.context_graph.store import list_graph_objects
from sera_message_intelligence.db import get_engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate evidence-grounded People / Relationship Radar from the durable context graph"
    )
    parser.add_argument("--output-root", default="reports/people-radar")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Session(get_engine()) as session:
        people = list_graph_objects(session, "person")
        opportunities = list_graph_objects(session, "opportunity")
        commitments = list_graph_objects(session, "commitment")

    radar = build_people_relationship_radar(
        person_records=people,
        opportunity_records=opportunities,
        commitment_records=commitments,
    )
    root = Path(args.output_root)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "people-radar.json"
    markdown_path = root / "people-radar.md"
    json_path.write_text(radar.model_dump_json(indent=2), encoding="utf-8")
    markdown_path.write_text(render_people_radar_markdown(radar), encoding="utf-8")

    print(
        json.dumps(
            {
                "generated_at": radar.generated_at.isoformat(),
                "people": len(radar.people),
                "relationships": len(radar.relationships),
                "people_with_active_opportunities": sum(
                    1 for item in radar.people if item.active_opportunity_ids
                ),
                "people_with_open_commitments": sum(
                    1 for item in radar.people if item.open_commitment_ids
                ),
                "json": str(json_path),
                "markdown": str(markdown_path),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
