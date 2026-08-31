from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sera_message_intelligence.context_graph.schemas import (
    ContextInference,
    SelfSignal,
)


NOW = datetime(2026, 8, 31, tzinfo=timezone.utc)


def test_confirmed_inference_requires_user_confirmation_ref() -> None:
    with pytest.raises(ValidationError):
        ContextInference(
            statement="This is confirmed",
            confidence=0.9,
            status="confirmed_by_user",
        )


def test_pattern_level_self_signal_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        SelfSignal(
            id="selfsig_1",
            created_at=NOW,
            updated_at=NOW,
            signal_type="attention",
            statement="AI product building is receiving more attention",
            window_start=NOW,
            window_end=NOW,
            confidence=0.8,
            evidence_level=2,
            source_diversity=1,
        )


def test_cross_source_self_signal_requires_source_diversity() -> None:
    with pytest.raises(ValidationError):
        SelfSignal(
            id="selfsig_2",
            created_at=NOW,
            updated_at=NOW,
            signal_type="interest_shift",
            statement="Product work is increasingly dominant",
            window_start=NOW,
            window_end=NOW,
            supporting_event_ids=["evt_1", "evt_2"],
            confidence=0.8,
            evidence_level=3,
            source_diversity=1,
        )


def test_level_four_self_signal_requires_user_confirmation() -> None:
    with pytest.raises(ValidationError):
        SelfSignal(
            id="selfsig_3",
            created_at=NOW,
            updated_at=NOW,
            signal_type="goal",
            statement="Building AI products is a durable priority",
            window_start=NOW,
            window_end=NOW,
            supporting_event_ids=["evt_1", "evt_2"],
            confidence=0.95,
            evidence_level=4,
            source_diversity=2,
            status="supported",
        )


def test_level_four_self_signal_accepts_explicit_confirmation() -> None:
    signal = SelfSignal(
        id="selfsig_4",
        created_at=NOW,
        updated_at=NOW,
        signal_type="goal",
        statement="Building AI products is a durable priority",
        window_start=NOW,
        window_end=NOW,
        supporting_event_ids=["evt_1", "evt_2"],
        confidence=1.0,
        evidence_level=4,
        source_diversity=2,
        status="confirmed_by_user",
        user_confirmation_ref="user_confirmation:2026-08-31",
    )
    assert signal.evidence_level == 4
    assert signal.status == "confirmed_by_user"


def test_self_signal_rejects_inverted_time_window() -> None:
    with pytest.raises(ValidationError):
        SelfSignal(
            id="selfsig_5",
            created_at=NOW,
            updated_at=NOW,
            signal_type="concern",
            statement="Repeated unresolved concern",
            window_start=datetime(2026, 9, 1, tzinfo=timezone.utc),
            window_end=NOW,
            supporting_event_ids=["evt_1"],
            confidence=0.7,
            evidence_level=2,
            source_diversity=1,
        )
