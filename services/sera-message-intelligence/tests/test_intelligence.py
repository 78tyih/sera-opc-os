from datetime import date, datetime, timezone

import pytest

from sera_message_intelligence.intelligence.chunker import chunk_messages
from sera_message_intelligence.intelligence.evidence import EvidenceError, materialize_item
from sera_message_intelligence.intelligence.pipeline import generate_daily_brief, summarize_chunks
from sera_message_intelligence.intelligence.renderer import render_html, render_markdown
from sera_message_intelligence.intelligence.schemas import CandidateItem, ImportanceComponents, IntelligenceMessage


def msg(id: int, conversation_id: str, text: str) -> IntelligenceMessage:
    return IntelligenceMessage(id=id, platform="wechat", account_id="wx1", conversation_id=conversation_id, conversation_name=f"Group {conversation_id}", sender_id="u1", sender_name="Alice", sent_at=datetime(2026, 8, 31, 1, id, tzinfo=timezone.utc), message_type="text", text_content=text)


def test_chunker_keeps_conversations_separate():
    chunks = chunk_messages([msg(1, "a", "one"), msg(2, "b", "two"), msg(3, "a", "three")], max_chars=1000)
    assert len(chunks) == 2
    assert {chunk.conversation_id for chunk in chunks} == {"a", "b"}
    assert all(len(set(m.conversation_id for m in chunk.messages)) == 1 for chunk in chunks)


def test_importance_formula_and_evidence_materialization():
    candidate = CandidateItem(category="must_handle", title="Act", summary="Do the thing", message_ids=[1], confidence=0.9, importance=ImportanceComponents(personal_relevance=1, actionability=1, urgency=1, novelty=0, source_weight=0.5))
    item = materialize_item(candidate, {1: msg(1, "a", "do it")})
    assert item.importance_score == 0.8
    assert item.sources[0].message_ids == [1]


def test_unknown_final_evidence_fails_closed():
    candidate = CandidateItem(category="important", title="Bad", summary="Unsupported", message_ids=[999], confidence=0.5, importance=ImportanceComponents(personal_relevance=1, actionability=0, urgency=0, novelty=0, source_weight=0))
    with pytest.raises(EvidenceError):
        materialize_item(candidate, {1: msg(1, "a", "known")})


class BadChunkLLM:
    def generate_json(self, *, system: str, prompt: str):
        return {"summary": "bad", "claims": [{"kind": "key_point", "text": "invented citation", "message_ids": [999]}]}


def test_unknown_chunk_claim_id_fails_closed():
    with pytest.raises(EvidenceError):
        summarize_chunks([msg(1, "a", "known")], BadChunkLLM())


class FakeLLM:
    def __init__(self): self.calls = 0
    def generate_json(self, *, system: str, prompt: str):
        self.calls += 1
        if "Summarize this conversation chunk" in prompt:
            if "[m:1]" in prompt:
                return {"summary": "group A discussed an action", "claims": [{"kind": "action", "text": "Follow up", "message_ids": [1]}]}
            return {"summary": "group B shared a risk", "claims": [{"kind": "risk", "text": "Watch risk", "message_ids": [2]}]}
        return {"executive_summary": "One action and one risk matter today.", "items": [
            {"category": "must_handle", "title": "Follow up", "summary": "A follow-up is required.", "message_ids": [1], "confidence": 0.95, "importance": {"personal_relevance": 1, "actionability": 1, "urgency": 0.8, "novelty": 0.5, "source_weight": 0.7}},
            {"category": "risks", "title": "Watch risk", "summary": "A risk was surfaced.", "message_ids": [2], "confidence": 0.9, "importance": {"personal_relevance": 0.8, "actionability": 0.4, "urgency": 0.7, "novelty": 0.6, "source_weight": 0.6}}
        ]}


def test_cross_group_brief_and_renderers():
    messages = [msg(1, "a", "please follow up"), msg(2, "b", "there is a risk")]
    brief = generate_daily_brief(brief_date=date(2026, 8, 31), messages=messages, llm=FakeLLM())
    assert brief.must_handle[0].sources[0].conversation_id == "a"
    assert brief.risks[0].sources[0].conversation_id == "b"
    md = render_markdown(brief)
    html = render_html(brief)
    assert "Evidence" in md and "Group a:1" in md
    assert "Intelligence Brief" in html and "Watch risk" in html
