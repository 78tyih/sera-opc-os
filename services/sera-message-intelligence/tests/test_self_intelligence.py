from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sera_message_intelligence.context_graph.self_intelligence import SelfIntelligenceSynthesizer
from sera_message_intelligence.models import ContextGraphChange


BASE = datetime(2026, 8, 25, 0, 0, tzinfo=timezone.utc)


class FakeLLM:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload

    def generate_json(self, *, system: str, prompt: str) -> dict[str, Any]:
        assert "never user-confirmed knowledge" in system
        assert "Validated graph changes" in prompt
        return self.payload


def graph_change(
    change_id: int,
    *,
    conversation_id: str,
    object_type: str = "opportunity",
    title: str | None = None,
) -> ContextGraphChange:
    occurred = BASE + timedelta(days=change_id)
    source_id = f"message:wechat:acct:{100 + change_id}"
    payload = {
        "id": f"object-{change_id}",
        "title": title or f"Opportunity {change_id}",
        "evidence_refs": [
            {
                "source_type": "message",
                "source_id": source_id,
                "platform": "wechat",
                "account_id": "acct",
                "conversation_id": conversation_id,
                "message_id": 100 + change_id,
                "occurred_at": occurred.isoformat(),
            }
        ],
    }
    return ContextGraphChange(
        change_id=change_id,
        object_id=f"object-{change_id}",
        object_type=object_type,
        change_kind="updated",
        changed_fields=["evidence_refs"],
        semantic_changes=["new_evidence"],
        evidence_ids=[source_id],
        before_payload={},
        after_payload=payload,
        batch_id="batch",
        effective_at=occurred,
        recorded_at=occurred,
    )


def test_cross_source_repeated_pattern_can_reach_level_three_supported() -> None:
    changes = [
        graph_change(1, conversation_id="group-a"),
        graph_change(2, conversation_id="group-b"),
        graph_change(3, conversation_id="group-a"),
    ]
    llm = FakeLLM(
        {
            "signals": [
                {
                    "signal_type": "attention",
                    "statement": "During this week, product-building opportunities repeatedly captured attention across multiple conversations.",
                    "supporting_change_ids": [1, 2, 3],
                    "contradicting_change_ids": [],
                    "confidence": 0.98,
                }
            ]
        }
    )

    result = SelfIntelligenceSynthesizer(llm).synthesize(
        changes=changes,
        window_start=BASE,
        window_end=BASE + timedelta(days=7),
    )

    assert result.rejected_candidates == []
    assert len(result.signals) == 1
    signal = result.signals[0]
    assert signal.evidence_level == 3
    assert signal.status == "supported"
    assert signal.source_diversity == 2
    assert signal.supporting_change_ids == [1, 2, 3]
    assert signal.confidence == 0.9
    assert len(signal.evidence_refs) == 3


def test_single_change_cannot_become_behavior_pattern() -> None:
    changes = [graph_change(1, conversation_id="group-a")]
    llm = FakeLLM(
        {
            "signals": [
                {
                    "signal_type": "behavior_pattern",
                    "statement": "During this window, follow-up behavior appears highly reactive.",
                    "supporting_change_ids": [1],
                    "contradicting_change_ids": [],
                    "confidence": 0.9,
                }
            ]
        }
    )

    result = SelfIntelligenceSynthesizer(llm).synthesize(
        changes=changes,
        window_start=BASE,
        window_end=BASE + timedelta(days=7),
    )
    assert result.signals == []
    assert "insufficient_pattern_evidence" in result.rejected_candidates[0]


def test_single_attention_signal_stays_level_two_and_confidence_is_capped() -> None:
    changes = [graph_change(1, conversation_id="group-a")]
    llm = FakeLLM(
        {
            "signals": [
                {
                    "signal_type": "attention",
                    "statement": "During this window, one new commercial opportunity drew attention.",
                    "supporting_change_ids": [1],
                    "contradicting_change_ids": [],
                    "confidence": 0.95,
                }
            ]
        }
    )

    result = SelfIntelligenceSynthesizer(llm).synthesize(
        changes=changes,
        window_start=BASE,
        window_end=BASE + timedelta(days=7),
    )
    signal = result.signals[0]
    assert signal.evidence_level == 2
    assert signal.status == "hypothesis"
    assert signal.confidence == 0.55


def test_unknown_change_id_is_rejected_fail_closed() -> None:
    changes = [graph_change(1, conversation_id="group-a")]
    llm = FakeLLM(
        {
            "signals": [
                {
                    "signal_type": "goal",
                    "statement": "During this window, shipping a product appears to be an active goal.",
                    "supporting_change_ids": [999],
                    "contradicting_change_ids": [],
                    "confidence": 0.8,
                }
            ]
        }
    )

    result = SelfIntelligenceSynthesizer(llm).synthesize(
        changes=changes,
        window_start=BASE,
        window_end=BASE + timedelta(days=7),
    )
    assert result.signals == []
    assert "unknown_change_id" in result.rejected_candidates[0]


def test_sensitive_or_clinical_personality_inference_is_rejected() -> None:
    changes = [
        graph_change(1, conversation_id="group-a"),
        graph_change(2, conversation_id="group-b"),
    ]
    llm = FakeLLM(
        {
            "signals": [
                {
                    "signal_type": "behavior_pattern",
                    "statement": "The user appears to have ADHD based on rapid project switching.",
                    "supporting_change_ids": [1, 2],
                    "contradicting_change_ids": [],
                    "confidence": 0.8,
                }
            ]
        }
    )

    result = SelfIntelligenceSynthesizer(llm).synthesize(
        changes=changes,
        window_start=BASE,
        window_end=BASE + timedelta(days=7),
    )
    assert result.signals == []
    assert "sensitive_or_clinical_inference" in result.rejected_candidates[0]
