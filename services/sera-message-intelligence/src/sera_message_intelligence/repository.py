from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import CollectorState, Message
from .schemas import CollectorHeartbeat, IngestResult, MessageEventV1


def _find_existing(session: Session, event: MessageEventV1) -> tuple[Message | None, str]:
    if event.external_message_id:
        existing = session.scalar(select(Message).where(Message.platform == event.platform, Message.account_id == event.account_id, Message.external_message_id == event.external_message_id))
        if existing:
            return existing, "external_message_id"
    existing = session.scalar(select(Message).where(Message.platform == event.platform, Message.account_id == event.account_id, Message.fingerprint == event.fingerprint))
    if existing:
        return existing, "fingerprint"
    return None, "none"


def ingest_message(session: Session, event: MessageEventV1) -> IngestResult:
    existing, reason = _find_existing(session, event)
    if existing:
        return IngestResult(id=existing.id, inserted=False, deduplicated_by=reason, fingerprint=existing.fingerprint)

    message = Message(
        schema_version=event.schema_version,
        platform=event.platform,
        account_id=event.account_id,
        collector_instance_id=event.collector_instance_id,
        external_message_id=event.external_message_id,
        conversation_id=event.conversation_id,
        conversation_type=event.conversation_type,
        conversation_name=event.conversation_name,
        sender_id=event.sender_id,
        sender_name=event.sender_name,
        sent_at=event.sent_at,
        received_at=event.received_at,
        message_type=event.message_type,
        text_content=event.text_content,
        attachments=[item.model_dump(mode="json", exclude_none=True) for item in event.attachments],
        raw_payload=event.raw_payload,
        fingerprint=event.fingerprint,
    )
    session.add(message)
    try:
        session.commit()
        session.refresh(message)
    except IntegrityError:
        session.rollback()
        existing, reason = _find_existing(session, event)
        if existing is None:
            raise
        return IngestResult(id=existing.id, inserted=False, deduplicated_by=reason, fingerprint=existing.fingerprint)

    return IngestResult(id=message.id, inserted=True, deduplicated_by="none", fingerprint=message.fingerprint)


def upsert_collector_heartbeat(session: Session, heartbeat: CollectorHeartbeat) -> CollectorState:
    state = session.get(CollectorState, heartbeat.collector_instance_id)
    now = datetime.now(timezone.utc)
    if state is None:
        state = CollectorState(
            collector_instance_id=heartbeat.collector_instance_id,
            account_id=heartbeat.account_id,
            platform=heartbeat.platform,
            status=heartbeat.status,
            started_at=now,
            last_heartbeat_at=now,
            last_message_at=heartbeat.last_message_at,
            last_checkpoint=heartbeat.last_checkpoint,
            messages_received=heartbeat.messages_received,
            errors=heartbeat.errors,
            updated_at=now,
        )
        session.add(state)
    else:
        state.account_id = heartbeat.account_id
        state.platform = heartbeat.platform
        state.status = heartbeat.status
        state.last_heartbeat_at = now
        state.last_message_at = heartbeat.last_message_at
        state.last_checkpoint = heartbeat.last_checkpoint
        state.messages_received = heartbeat.messages_received
        state.errors = heartbeat.errors
        state.updated_at = now
    session.commit()
    return state


def list_collector_states(session: Session) -> list[CollectorState]:
    return list(session.scalars(select(CollectorState).order_by(CollectorState.account_id.asc(), CollectorState.collector_instance_id.asc())).all())


def list_messages_between(session: Session, start: datetime, end: datetime) -> list[Message]:
    stmt = select(Message).where(Message.sent_at >= start, Message.sent_at < end).order_by(Message.sent_at.asc(), Message.id.asc())
    return list(session.scalars(stmt).all())
