from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ConversationType = Literal["direct", "group", "channel", "unknown"]
MessageType = Literal["text", "image", "voice", "file", "video", "system", "unknown"]
CollectorStatus = Literal["starting", "online", "degraded", "offline", "error"]


class AttachmentRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    uri: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None


class MessageEventV1(BaseModel):
    """Canonical inbound message envelope shared by all collectors."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    platform: str = Field(min_length=1, max_length=64)
    account_id: str = Field(min_length=1, max_length=255)
    collector_instance_id: str = Field(min_length=1, max_length=255)
    external_message_id: str | None = Field(default=None, max_length=512)
    conversation_id: str = Field(min_length=1, max_length=512)
    conversation_type: ConversationType = "unknown"
    conversation_name: str | None = Field(default=None, max_length=512)
    sender_id: str = Field(min_length=1, max_length=512)
    sender_name: str | None = Field(default=None, max_length=512)
    sent_at: datetime
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_type: MessageType = "text"
    text_content: str | None = None
    attachments: list[AttachmentRef] = Field(default_factory=list)
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    @model_validator(mode="after")
    def ensure_fingerprint(self) -> "MessageEventV1":
        if self.fingerprint:
            return self
        canonical = {
            "platform": self.platform,
            "account_id": self.account_id,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "sent_at": self.sent_at.astimezone(timezone.utc).isoformat(),
            "message_type": self.message_type,
            "text_content": self.text_content or "",
            "attachments": [item.model_dump(mode="json", exclude_none=True) for item in self.attachments],
        }
        payload = json.dumps(canonical, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        self.fingerprint = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return self


class IngestResult(BaseModel):
    id: int
    inserted: bool
    deduplicated_by: Literal["none", "external_message_id", "fingerprint"]
    fingerprint: str


class CollectorHeartbeat(BaseModel):
    collector_instance_id: str
    account_id: str
    platform: str
    status: CollectorStatus
    last_checkpoint: str | None = None
    last_message_at: datetime | None = None
    messages_received: int = 0
    errors: int = 0


class CollectorHeartbeatResult(BaseModel):
    collector_instance_id: str
    status: CollectorStatus
    updated: bool = True
