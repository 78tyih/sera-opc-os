CREATE TABLE IF NOT EXISTS context_graph_changes (
    change_id BIGSERIAL PRIMARY KEY,
    object_id VARCHAR(128) NOT NULL,
    object_type VARCHAR(32) NOT NULL,
    change_kind VARCHAR(32) NOT NULL,
    changed_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
    semantic_changes JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    before_payload JSONB,
    after_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    batch_id VARCHAR(128),
    effective_at TIMESTAMPTZ NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_context_graph_changes_effective_at
    ON context_graph_changes (effective_at DESC);
CREATE INDEX IF NOT EXISTS ix_context_graph_changes_object_effective
    ON context_graph_changes (object_id, effective_at DESC);
CREATE INDEX IF NOT EXISTS ix_context_graph_changes_batch_id
    ON context_graph_changes (batch_id);
CREATE INDEX IF NOT EXISTS ix_context_graph_changes_object_type
    ON context_graph_changes (object_type);
CREATE INDEX IF NOT EXISTS ix_context_graph_changes_change_kind
    ON context_graph_changes (change_kind);
