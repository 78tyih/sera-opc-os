from __future__ import annotations
from datetime import timezone
from ...schemas import MessageEventV1
from .raw_message import RawWechatMessage

_ALLOWED_TYPES={"text","image","voice","file","video","system","unknown"}

def normalize_wechat_message(raw: RawWechatMessage, *, account_id: str, collector_instance_id: str) -> MessageEventV1:
    sent_at=raw.sent_at if raw.sent_at.tzinfo else raw.sent_at.replace(tzinfo=timezone.utc)
    message_type=raw.message_type if raw.message_type in _ALLOWED_TYPES else "unknown"
    return MessageEventV1(
        platform="wechat",
        account_id=account_id,
        collector_instance_id=collector_instance_id,
        external_message_id=raw.external_message_id,
        conversation_id=raw.conversation_id,
        conversation_type="group",
        conversation_name=raw.conversation_name,
        sender_id=raw.sender_id,
        sender_name=raw.sender_name,
        sent_at=sent_at,
        message_type=message_type,
        text_content=raw.text_content,
        raw_payload=raw.raw_payload,
    )
