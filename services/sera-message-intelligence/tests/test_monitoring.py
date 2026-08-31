from datetime import datetime, timedelta, timezone
from sera_message_intelligence.models import CollectorState
from sera_message_intelligence.monitoring import collector_state_view


def state(last_heartbeat_at, status="online"):
    return CollectorState(collector_instance_id="c1",account_id="wx1",platform="wechat",status=status,started_at=last_heartbeat_at,last_heartbeat_at=last_heartbeat_at,last_message_at=None,last_checkpoint="1",messages_received=10,errors=0,updated_at=last_heartbeat_at)


def test_fresh_heartbeat_preserves_reported_status():
    now=datetime(2026,8,31,8,0,tzinfo=timezone.utc)
    view=collector_state_view(state(now-timedelta(seconds=30)),stale_seconds=90,now=now)
    assert view.reported_status=="online" and view.effective_status=="online"
    assert view.heartbeat_age_seconds==30


def test_stale_heartbeat_is_effectively_offline():
    now=datetime(2026,8,31,8,0,tzinfo=timezone.utc)
    view=collector_state_view(state(now-timedelta(seconds=120)),stale_seconds=90,now=now)
    assert view.reported_status=="online" and view.effective_status=="offline"
