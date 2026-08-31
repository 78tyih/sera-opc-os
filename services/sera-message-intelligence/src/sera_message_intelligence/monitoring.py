from __future__ import annotations
from datetime import datetime, timezone
from .models import CollectorState
from .schemas import CollectorStateView


def collector_state_view(state: CollectorState, *, stale_seconds: int, now: datetime | None = None) -> CollectorStateView:
    now=now or datetime.now(timezone.utc)
    last=state.last_heartbeat_at
    if last.tzinfo is None:
        last=last.replace(tzinfo=timezone.utc)
    age=max(0.0,(now-last).total_seconds())
    reported=state.status
    effective="offline" if age>stale_seconds else reported
    return CollectorStateView(
        collector_instance_id=state.collector_instance_id,
        account_id=state.account_id,
        platform=state.platform,
        reported_status=reported,
        effective_status=effective,
        started_at=state.started_at,
        last_heartbeat_at=state.last_heartbeat_at,
        last_message_at=state.last_message_at,
        last_checkpoint=state.last_checkpoint,
        messages_received=state.messages_received,
        errors=state.errors,
        heartbeat_age_seconds=round(age,3),
    )
