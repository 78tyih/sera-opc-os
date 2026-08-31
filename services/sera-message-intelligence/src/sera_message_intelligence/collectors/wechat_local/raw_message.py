from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass(slots=True)
class RawWechatMessage:
    external_message_id: str | None
    conversation_id: str
    conversation_name: str | None
    sender_id: str
    sender_name: str | None
    sent_at: datetime
    message_type: str = "text"
    text_content: str | None = None
    raw_payload: dict[str, Any] = field(default_factory=dict)
