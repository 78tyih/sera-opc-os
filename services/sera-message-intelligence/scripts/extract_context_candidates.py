from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from sera_message_intelligence.config import get_settings
from sera_message_intelligence.context_graph.pipeline import extract_context_candidates
from sera_message_intelligence.context_graph.store import upsert_context_result
from sera_message_intelligence.db import get_engine
from sera_message_intelligence.intelligence.schemas import IntelligenceMessage
from sera_message_intelligence.llm.client import OpenAICompatibleLLM
from sera_message_intelligence.repository import list_messages_between


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract evidence-backed Personal Context Graph candidates"
    )
    parser.add_argument("--date", help="Local extraction date in YYYY-MM-DD. Defaults to yesterday.")
    parser.add_argument("--output-root", default="reports")
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Conservatively resolve exact matches and upsert candidates into context_graph_objects.",
    )
    return parser.parse_args()


def resolve_day(raw: str | None, tz: ZoneInfo) -> date:
    if raw:
        return date.fromisoformat(raw)
    return (datetime.now(tz) - timedelta(days=1)).date()


def utc_bounds(day: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
    start_local = datetime.combine(day, time.min, tzinfo=tz)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def to_intelligence_message(row) -> IntelligenceMessage:
    return IntelligenceMessage(
        id=row.id,
        platform=row.platform,
        account_id=row.account_id,
        conversation_id=row.conversation_id,
        conversation_name=row.conversation_name,
        sender_id=row.sender_id,
        sender_name=row.sender_name,
        sent_at=row.sent_at,
        message_type=row.message_type,
        text_content=row.text_content,
    )


def main() -> None:
    args = parse_args()
    settings = get_settings()
    tz = ZoneInfo(settings.report_timezone)
    day = resolve_day(args.date, tz)
    start, end = utc_bounds(day, tz)
    engine = get_engine()

    with Session(engine) as session:
        rows = list_messages_between(session, start, end)
    messages = [to_intelligence_message(row) for row in rows]

    output = Path(args.output_root) / day.isoformat()
    output.mkdir(parents=True, exist_ok=True)
    output_file = output / "context-candidates.json"

    if not messages:
        output_file.write_text(
            json.dumps(
                {
                    "persons": [],
                    "events": [],
                    "opportunities": [],
                    "commitments": [],
                    "rejected_candidates": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "date": day.isoformat(),
                    "messages": 0,
                    "persisted": False,
                    "output": str(output_file),
                },
                ensure_ascii=False,
            )
        )
        return

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
        result = extract_context_candidates(
            messages=messages,
            llm=llm,
            max_chars=args.max_chars,
        )
    finally:
        llm.close()

    output_file.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    graph_summary = None
    if args.persist:
        with Session(engine) as session:
            graph_summary = upsert_context_result(session, result)

    response = {
        "date": day.isoformat(),
        "messages": len(messages),
        "persons": len(result.persons),
        "events": len(result.events),
        "opportunities": len(result.opportunities),
        "commitments": len(result.commitments),
        "rejected": len(result.rejected_candidates),
        "persisted": args.persist,
        "output": str(output_file),
    }
    if graph_summary is not None:
        response["graph_created"] = graph_summary.created
        response["graph_updated"] = graph_summary.updated

    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
