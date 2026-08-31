from __future__ import annotations

from sera_message_intelligence.intelligence.chunker import chunk_messages
from sera_message_intelligence.intelligence.schemas import IntelligenceMessage
from sera_message_intelligence.llm.client import StructuredLLM

from .extraction import ContextExtractionResult, ContextGraphExtractor
from .schemas import Person


def _merge_person(existing: Person, incoming: Person) -> Person:
    evidence_by_id = {ref.source_id: ref for ref in existing.evidence_refs}
    evidence_by_id.update({ref.source_id: ref for ref in incoming.evidence_refs})

    aliases = list(dict.fromkeys([*existing.aliases, *incoming.aliases]))
    if incoming.display_name != existing.display_name and incoming.display_name not in aliases:
        aliases.append(existing.display_name)

    identities: dict[str, list[str]] = {
        platform: list(values) for platform, values in existing.identities.items()
    }
    for platform, values in incoming.identities.items():
        identities[platform] = list(dict.fromkeys([*identities.get(platform, []), *values]))

    display_name = incoming.display_name
    last_interaction = existing.last_meaningful_interaction_at
    if (
        incoming.last_meaningful_interaction_at is not None
        and (
            last_interaction is None
            or incoming.last_meaningful_interaction_at >= last_interaction
        )
    ):
        last_interaction = incoming.last_meaningful_interaction_at
    else:
        display_name = existing.display_name

    return existing.model_copy(
        update={
            "updated_at": max(existing.updated_at, incoming.updated_at),
            "evidence_refs": sorted(
                evidence_by_id.values(),
                key=lambda ref: (ref.occurred_at is None, ref.occurred_at, ref.source_id),
            ),
            "aliases": aliases,
            "identities": identities,
            "display_name": display_name,
            "last_meaningful_interaction_at": last_interaction,
        }
    )


def extract_context_candidates(
    *,
    messages: list[IntelligenceMessage],
    llm: StructuredLLM,
    max_chars: int = 12000,
) -> ContextExtractionResult:
    """Extract bounded evidence-backed candidates across conversations.

    Each chunk is processed independently so model context remains bounded. Person
    objects are deterministically merged by stable ID. Other objects remain signal
    candidates until a later entity-resolution/upsert stage decides whether they
    represent the same durable object.
    """

    if not messages:
        return ContextExtractionResult()

    extractor = ContextGraphExtractor(llm)
    people_by_id: dict[str, Person] = {}
    result = ContextExtractionResult()

    for chunk in chunk_messages(messages, max_chars=max_chars):
        extracted = extractor.extract(chunk.messages)
        for person in extracted.persons:
            if person.id in people_by_id:
                people_by_id[person.id] = _merge_person(people_by_id[person.id], person)
            else:
                people_by_id[person.id] = person
        result.events.extend(extracted.events)
        result.opportunities.extend(extracted.opportunities)
        result.commitments.extend(extracted.commitments)
        result.rejected_candidates.extend(extracted.rejected_candidates)

    result.persons = list(people_by_id.values())
    return result
