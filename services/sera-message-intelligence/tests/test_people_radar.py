from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sera_message_intelligence.context_graph.people_radar import build_people_relationship_radar
from sera_message_intelligence.context_graph.schemas import (
    Commitment,
    ContextEvidenceRef,
    Opportunity,
    Person,
)
from sera_message_intelligence.models import ContextGraphObject


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


def evidence(person_id: str, message_id: int, at: datetime) -> ContextEvidenceRef:
    return ContextEvidenceRef(
        source_type="message",
        source_id=f"message:wechat:acct:{message_id}:{person_id}",
        platform="wechat",
        account_id="acct",
        conversation_id="group",
        message_id=message_id,
        occurred_at=at,
    )


def person_record(
    person_id: str,
    name: str,
    *,
    days_ago: int,
    evidence_count: int,
) -> ContextGraphObject:
    at = NOW - timedelta(days=days_ago)
    ref = evidence(person_id, 10 + evidence_count, at)
    person = Person(
        id=person_id,
        created_at=at,
        updated_at=at,
        evidence_refs=[ref],
        observations=[f"Observed sender identity {person_id}"],
        inferences=[],
        display_name=name,
        aliases=[],
        identities={"wechat": [person_id]},
        organization=None,
        roles=[],
        locations=[],
        interests=[],
        expertise=[],
        relationship_ids=[],
        opportunity_ids=[],
        project_ids=[],
        commitment_ids=[],
        last_meaningful_interaction_at=at,
        confidence=1.0,
    )
    return ContextGraphObject(
        object_id=person_id,
        object_type="person",
        canonical_key=f"key:{person_id}",
        payload=person.model_dump(mode="json"),
        first_seen_at=at,
        last_seen_at=at,
        evidence_count=evidence_count,
        created_at=at,
        updated_at=at,
    )


def opportunity_record(
    object_id: str,
    people: list[str],
    *,
    days_ago: int = 1,
    stage: str = "signal",
) -> ContextGraphObject:
    at = NOW - timedelta(days=days_ago)
    ref = evidence("opportunity", 100, at)
    obj = Opportunity(
        id=object_id,
        created_at=at,
        updated_at=at,
        evidence_refs=[ref],
        observations=[],
        inferences=[],
        title="High-fit partnership",
        opportunity_type="partnership",
        stage=stage,
        person_ids=people,
        organization_ids=[],
        project_ids=[],
        problem="Need distribution",
        proposed_value="Joint distribution",
        estimated_value=None,
        currency=None,
        urgency=0.9,
        fit=0.95,
        probability=0.75,
        next_actions=["Schedule call"],
        risk_ids=[],
        first_seen_at=at,
        last_signal_at=at,
    )
    return ContextGraphObject(
        object_id=object_id,
        object_type="opportunity",
        canonical_key=f"key:{object_id}",
        payload=obj.model_dump(mode="json"),
        first_seen_at=at,
        last_seen_at=at,
        evidence_count=4,
        created_at=at,
        updated_at=at,
    )


def commitment_record(
    object_id: str,
    owner: str,
    beneficiary: str,
    *,
    overdue: bool = False,
    status: str = "open",
) -> ContextGraphObject:
    at = NOW - timedelta(hours=2)
    ref = evidence("commitment", 200, at)
    due_at = NOW - timedelta(hours=1) if overdue else NOW + timedelta(days=2)
    obj = Commitment(
        id=object_id,
        created_at=at,
        updated_at=at,
        evidence_refs=[ref],
        observations=[],
        inferences=[],
        owner_person_id=owner,
        beneficiary_person_ids=[beneficiary],
        summary="Send requested materials",
        status=status,
        due_at=due_at,
        related_person_ids=[beneficiary],
        related_project_ids=[],
        related_opportunity_ids=[],
        confidence=0.95,
    )
    return ContextGraphObject(
        object_id=object_id,
        object_type="commitment",
        canonical_key=f"key:{object_id}",
        payload=obj.model_dump(mode="json"),
        first_seen_at=at,
        last_seen_at=at,
        evidence_count=3,
        created_at=at,
        updated_at=at,
    )


def test_people_radar_prioritizes_business_signal_over_chat_volume() -> None:
    alice = person_record("person_alice", "Alice", days_ago=2, evidence_count=3)
    chatter = person_record("person_chatter", "Chatter", days_ago=1, evidence_count=50)
    opportunity = opportunity_record("opp_1", ["person_alice"])

    radar = build_people_relationship_radar(
        person_records=[chatter, alice],
        opportunity_records=[opportunity],
        commitment_records=[],
        now=NOW,
    )

    assert radar.people[0].person_id == "person_alice"
    assert "active_opportunity" in radar.people[0].reasons
    assert radar.people[0].attention_score > radar.people[1].attention_score


def test_relationship_edge_requires_explicit_shared_context() -> None:
    alice = person_record("person_alice", "Alice", days_ago=1, evidence_count=3)
    bob = person_record("person_bob", "Bob", days_ago=1, evidence_count=3)

    without_context = build_people_relationship_radar(
        person_records=[alice, bob],
        opportunity_records=[],
        commitment_records=[],
        now=NOW,
    )
    assert without_context.relationships == []

    shared = opportunity_record("opp_shared", ["person_alice", "person_bob"])
    with_context = build_people_relationship_radar(
        person_records=[alice, bob],
        opportunity_records=[shared],
        commitment_records=[],
        now=NOW,
    )

    assert len(with_context.relationships) == 1
    edge = with_context.relationships[0]
    assert {edge.person_a_id, edge.person_b_id} == {"person_alice", "person_bob"}
    assert edge.shared_opportunity_ids == ["opp_shared"]
    assert "shared_active_opportunity" in edge.reasons


def test_overdue_commitment_surfaces_on_person_and_relationship() -> None:
    me = person_record("person_me", "Me", days_ago=0, evidence_count=2)
    alice = person_record("person_alice", "Alice", days_ago=1, evidence_count=2)
    commitment = commitment_record(
        "commit_overdue",
        "person_me",
        "person_alice",
        overdue=True,
    )

    radar = build_people_relationship_radar(
        person_records=[me, alice],
        opportunity_records=[],
        commitment_records=[commitment],
        now=NOW,
    )

    alice_item = next(item for item in radar.people if item.person_id == "person_alice")
    assert alice_item.overdue_commitment_ids == ["commit_overdue"]
    assert "overdue_commitment" in alice_item.reasons

    assert len(radar.relationships) == 1
    edge = radar.relationships[0]
    assert edge.overdue_commitment_ids == ["commit_overdue"]
    assert "overdue_commitment_link" in edge.reasons
