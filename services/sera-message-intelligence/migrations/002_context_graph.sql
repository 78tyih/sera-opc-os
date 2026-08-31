CREATE TABLE IF NOT EXISTS context_graph_objects (
    object_id VARCHAR(128) PRIMARY KEY,
    object_type VARCHAR(32) NOT NULL,
    canonical_key VARCHAR(128) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    first_seen_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    evidence_count BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_context_graph_type_key UNIQUE (object_type, canonical_key)
);

CREATE INDEX IF NOT EXISTS ix_context_graph_object_type ON context_graph_objects (object_type);
CREATE INDEX IF NOT EXISTS ix_context_graph_last_seen ON context_graph_objects (last_seen_at DESC);
