CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    schema_version VARCHAR(16) NOT NULL DEFAULT '1.0',
    platform VARCHAR(64) NOT NULL,
    account_id VARCHAR(255) NOT NULL,
    collector_instance_id VARCHAR(255) NOT NULL,
    external_message_id VARCHAR(512),
    conversation_id VARCHAR(512) NOT NULL,
    conversation_type VARCHAR(32) NOT NULL DEFAULT 'unknown',
    conversation_name VARCHAR(512),
    sender_id VARCHAR(512) NOT NULL,
    sender_name VARCHAR(512),
    sent_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL,
    message_type VARCHAR(32) NOT NULL,
    text_content TEXT,
    attachments JSONB NOT NULL DEFAULT '[]'::jsonb,
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    fingerprint CHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_messages_external_id UNIQUE (platform, account_id, external_message_id),
    CONSTRAINT uq_messages_fingerprint UNIQUE (platform, account_id, fingerprint)
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_sent_at ON messages (conversation_id, sent_at DESC);
CREATE INDEX IF NOT EXISTS ix_messages_account_sent_at ON messages (account_id, sent_at DESC);
