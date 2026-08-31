from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from sera_message_intelligence.config import get_settings
from sera_message_intelligence.db import get_engine
from sera_message_intelligence.intelligence.pipeline import generate_daily_brief
from sera_message_intelligence.intelligence.renderer import render_html, render_markdown
from sera_message_intelligence.intelligence.schemas import DailyBrief, IntelligenceMessage
from sera_message_intelligence.llm.client import OpenAICompatibleLLM
from sera_message_intelligence.repository import list_messages_between


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate one evidence-backed Personal Intelligence Brief")
    parser.add_argument("--date", help="Local report date in YYYY-MM-DD. Defaults to yesterday.")
    parser.add_argument("--output-root", default="reports")
    parser.add_argument("--max-chars", type=int, default=12000)
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


def write_outputs(brief: DailyBrief, root: Path) -> Path:
    output = root / brief.date.isoformat()
    output.mkdir(parents=True, exist_ok=True)
    (output / "brief.json").write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    (output / "brief.md").write_text(render_markdown(brief), encoding="utf-8")
    (output / "brief.html").write_text(render_html(brief), encoding="utf-8")
    return output


def main() -> None:
    args = parse_args()
    settings = get_settings()
    tz = ZoneInfo(settings.report_timezone)
    day = resolve_day(args.date, tz)
    start, end = utc_bounds(day, tz)

    with Session(get_engine()) as session:
        rows = list_messages_between(session, start, end)
    messages = [to_intelligence_message(row) for row in rows]

    if not messages:
        brief = DailyBrief(date=day, executive_summary="No messages were captured for this report window.")
    else:
        missing = [name for name, value in (("SMI_LLM_BASE_URL", settings.llm_base_url), ("SMI_LLM_API_KEY", settings.llm_api_key), ("SMI_LLM_MODEL", settings.llm_model)) if not value]
        if missing:
            raise SystemExit("Missing LLM settings: " + ", ".join(missing))
        llm = OpenAICompatibleLLM(base_url=settings.llm_base_url, api_key=settings.llm_api_key, model=settings.llm_model)
        try:
            brief = generate_daily_brief(brief_date=day, messages=messages, llm=llm, max_chars=args.max_chars)
        finally:
            llm.close()

    output = write_outputs(brief, Path(args.output_root))
    print(json.dumps({"date": day.isoformat(), "messages": len(messages), "output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
