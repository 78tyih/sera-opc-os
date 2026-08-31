from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("platform", "account_id", "external_message_id", name="uq_messages_external_id"),
        UniqueConstraint("platform", "account_id", "fingerprint", name="uq_messages_fingerprint"),
        Index("ix_messages_conversation_sent_at", "conversation_id", "sent_at"),
        Index("ix_messages_account_sent_at", "account_id", "sent_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    schema_version: Mapped[str] = mapped_column(String(16), nullable=False, default="1.0")
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    collector_instance_id: Mapped[str] = mapped_column(String(255), nullable=False)
    external_message_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    conversation_id: Mapped[str] = mapped_column(String(512), nullable=False)
    conversation_type: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    conversation_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sender_id: Mapped[str] = mapped_column(String(512), nullable=False)
    sender_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message_type: Mapped[str] = mapped_column(String(32), nullable=False)
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class CollectorState(Base):
    __tablename__ = "collector_states"

    collector_instance_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_checkpoint: Mapped[str | None] = mapped_column(Text, nullable=True)
    messages_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errors: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
