from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from sera_message_intelligence.config import get_settings
from sera_message_intelligence.context_graph.change_feed import (
    build_world_change_brief,
    render_world_change_markdown,
)
from sera_message_intelligence.context_graph.change_history import list_graph_changes
from sera_message_intelligence.db import get_engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic Personal Intelligence Brief V2 from graph changes"
    )
    parser.add_argument("--date", help="Local report date in YYYY-MM-DD. Defaults to yesterday.")
    parser.add_argument("--output-root", default="reports")
    return parser.parse_args()


def resolve_day(raw: str | None, tz: ZoneInfo) -> date:
    if raw:
        return date.fromisoformat(raw)
    return (datetime.now(tz) - timedelta(days=1)).date()


def utc_bounds(day: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
    start_local = datetime.combine(day, time.min, tzinfo=tz)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def main() -> None:
    args = parse_args()
    settings = get_settings()
    tz = ZoneInfo(settings.report_timezone)
    day = resolve_day(args.date, tz)
    start, end = utc_bounds(day, tz)

    with Session(get_engine()) as session:
        changes = list_graph_changes(session, start=start, end=end)

    brief = build_world_change_brief(
        changes=changes,
        window_start=start,
        window_end=end,
        as_of=end,
    )

    output = Path(args.output_root) / day.isoformat()
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "world-changes.json"
    markdown_path = output / "world-changes.md"
    json_path.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    markdown_path.write_text(render_world_change_markdown(brief), encoding="utf-8")

    print(
        json.dumps(
            {
                "date": day.isoformat(),
                "changes": brief.total_changes,
                "new_opportunities": len(brief.new_opportunities),
                "opportunity_changes": len(brief.opportunity_changes),
                "commitment_changes": len(brief.commitment_changes),
                "people_changes": len(brief.people_changes),
                "event_changes": len(brief.event_changes),
                "json": str(json_path),
                "markdown": str(markdown_path),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
