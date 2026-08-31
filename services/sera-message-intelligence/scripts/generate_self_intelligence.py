from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from sera_message_intelligence.config import get_settings
from sera_message_intelligence.context_graph.change_history import list_graph_changes
from sera_message_intelligence.context_graph.self_intelligence import (
    SelfIntelligenceResult,
    SelfIntelligenceSynthesizer,
)
from sera_message_intelligence.context_graph.self_renderer import (
    render_self_intelligence_markdown,
)
from sera_message_intelligence.context_graph.store import upsert_self_signals
from sera_message_intelligence.db import get_engine
from sera_message_intelligence.llm.client import OpenAICompatibleLLM


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate evidence-gated Self Intelligence from durable graph changes"
    )
    parser.add_argument(
        "--end-date",
        help="Last local day included in YYYY-MM-DD. Defaults to yesterday.",
    )
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--output-root", default="reports/self-intelligence")
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist validated SelfSignals into the durable Personal Context Graph.",
    )
    return parser.parse_args()


def resolve_window(
    raw_end: str | None,
    days: int,
    tz: ZoneInfo,
) -> tuple[date, date, datetime, datetime]:
    if days < 1:
        raise SystemExit("--days must be >= 1")
    end_day = date.fromisoformat(raw_end) if raw_end else (datetime.now(tz) - timedelta(days=1)).date()
    start_day = end_day - timedelta(days=days - 1)
    start_local = datetime.combine(start_day, time.min, tzinfo=tz)
    end_local = datetime.combine(end_day + timedelta(days=1), time.min, tzinfo=tz)
    return (
        start_day,
        end_day,
        start_local.astimezone(timezone.utc),
        end_local.astimezone(timezone.utc),
    )


def main() -> None:
    args = parse_args()
    settings = get_settings()
    tz = ZoneInfo(settings.report_timezone)
    start_day, end_day, start, end = resolve_window(args.end_date, args.days, tz)

    with Session(get_engine()) as session:
        # Do not recursively derive Self Intelligence from prior SelfSignal changes.
        changes = [
            change
            for change in list_graph_changes(session, start=start, end=end)
            if change.object_type != "self_signal"
        ]

    if not changes:
        result = SelfIntelligenceResult()
    else:
        missing = [
            name
            for name, value in (
                ("SMI_LLM_BASE_URL", settings.llm_base_url),
                ("SMI_LLM_API_KEY", settings.llm_api_key),
                ("SMI_LLM_MODEL", settings.llm_model),
            )
            if not value
        ]
        if missing:
            raise SystemExit("Missing LLM settings: " + ", ".join(missing))

        llm = OpenAICompatibleLLM(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
        try:
            result = SelfIntelligenceSynthesizer(llm).synthesize(
                changes=changes,
                window_start=start,
                window_end=end,
            )
        finally:
            llm.close()

    persisted = None
    if args.persist and result.signals:
        with Session(get_engine()) as session:
            persisted = upsert_self_signals(session, result.signals)

    output = Path(args.output_root) / f"{start_day.isoformat()}_to_{end_day.isoformat()}"
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "self-intelligence.json"
    markdown_path = output / "self-intelligence.md"
    json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    markdown_path.write_text(
        render_self_intelligence_markdown(
            result,
            window_start=start,
            window_end=end,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "window_start": start_day.isoformat(),
                "window_end": end_day.isoformat(),
                "graph_changes": len(changes),
                "signals": len(result.signals),
                "rejected": len(result.rejected_candidates),
                "persisted": persisted.model_dump(mode="json") if persisted else None,
                "json": str(json_path),
                "markdown": str(markdown_path),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
