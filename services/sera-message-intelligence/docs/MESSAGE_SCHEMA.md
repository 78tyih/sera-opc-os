# MessageEventV1

`MessageEventV1` is the single canonical inbound envelope.

Required identity dimensions: `platform`, `account_id`, `collector_instance_id`, `conversation_id`, `sender_id`, `sent_at`.

Preferred upstream identity is `external_message_id`. Every event also carries a deterministic SHA-256 `fingerprint`.

## Idempotency

Primary semantic key: `(platform, account_id, external_message_id)`.

Fallback key: `(platform, account_id, fingerprint)`.

The database enforces both, and the repository handles race-condition integrity errors by re-reading the winner.

## Provenance

`raw_payload` preserves adapter-native source data for debugging and later schema evolution. It is not the canonical business interface.
