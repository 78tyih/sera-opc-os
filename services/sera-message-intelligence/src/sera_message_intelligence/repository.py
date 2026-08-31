from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Message
from .schemas import IngestResult, MessageEventV1


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
