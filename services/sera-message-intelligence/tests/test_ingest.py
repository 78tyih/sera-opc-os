from datetime import datetime, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from sera_message_intelligence.db import Base
from sera_message_intelligence.models import Message
from sera_message_intelligence.repository import ingest_message
from sera_message_intelligence.schemas import MessageEventV1


def _engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return engine


def _event(**overrides):
    payload = {
        "platform": "wechat",
        "account_id": "wx-account-01",
        "collector_instance_id": "wechat-local-01",
        "external_message_id": "msg-001",
        "conversation_id": "group-001",
        "conversation_type": "group",
        "conversation_name": "Core Test Group",
        "sender_id": "wxid-001",
        "sender_name": "Alice",
        "sent_at": datetime(2026, 8, 31, 7, 0, tzinfo=timezone.utc),
        "message_type": "text",
        "text_content": "ship the P0 message core",
    }
    payload.update(overrides)
    return MessageEventV1(**payload)


def test_same_external_message_id_is_idempotent():
    engine = _engine()
    with Session(engine) as session:
        first = ingest_message(session, _event())
        second = ingest_message(session, _event(text_content="changed transport payload"))
        count = session.scalar(select(func.count()).select_from(Message))
    assert first.inserted is True
    assert second.inserted is False
    assert second.deduplicated_by == "external_message_id"
    assert second.id == first.id
    assert count == 1


def test_fingerprint_deduplicates_when_external_id_is_missing():
    engine = _engine()
    event = _event(external_message_id=None)
    with Session(engine) as session:
        first = ingest_message(session, event)
        second = ingest_message(session, _event(external_message_id=None))
        count = session.scalar(select(func.count()).select_from(Message))
    assert first.inserted is True
    assert second.inserted is False
    assert second.deduplicated_by == "fingerprint"
    assert count == 1


def test_distinct_messages_are_inserted():
    engine = _engine()
    with Session(engine) as session:
        first = ingest_message(session, _event())
        second = ingest_message(session, _event(external_message_id="msg-002", text_content="next message"))
        count = session.scalar(select(func.count()).select_from(Message))
    assert first.inserted is True
    assert second.inserted is True
    assert count == 2
