from __future__ import annotations
import json
from datetime import date
from pydantic import TypeAdapter
from ..llm.client import StructuredLLM
from .chunker import chunk_messages, format_chunk
from .evidence import EvidenceError, materialize_item
from .prompts import CHUNK_SYSTEM, MERGE_SYSTEM, chunk_prompt, merge_prompt
from .schemas import CandidateItem, ChunkClaim, ChunkSummary, DailyBrief, IntelligenceMessage

_candidate_adapter=TypeAdapter(list[CandidateItem])
_claim_adapter=TypeAdapter(list[ChunkClaim])

def summarize_chunks(messages:list[IntelligenceMessage], llm:StructuredLLM, max_chars:int=12000)->list[ChunkSummary]:
    results=[]
    for chunk in chunk_messages(messages,max_chars=max_chars):
        raw=llm.generate_json(system=CHUNK_SYSTEM,prompt=chunk_prompt(format_chunk(chunk)))
        claims=_claim_adapter.validate_python(raw.get("claims",[]))
        allowed=set(chunk.message_ids)
        for claim in claims:
            missing=[mid for mid in claim.message_ids if mid not in allowed]
            if missing:
                raise EvidenceError(f"chunk {chunk.chunk_id} cited unknown message ids: {missing}")
        results.append(ChunkSummary(chunk_id=chunk.chunk_id,conversation_id=chunk.conversation_id,conversation_name=chunk.conversation_name,message_ids=chunk.message_ids,summary=str(raw.get("summary","")),claims=claims))
    return results

def _validated_claim_payload(summaries:list[ChunkSummary])->tuple[list[dict],set[int]]:
    """Expose only evidence-bound claims to the cross-group merge stage.

    Full chunk message-id lists and free-form chunk summaries are deliberately
    excluded so the merge model cannot cite an unrelated-but-real message.
    """
    payload=[]
    allowed_ids:set[int]=set()
    for summary in summaries:
        claims=[claim.model_dump(mode="json") for claim in summary.claims]
        for claim in summary.claims:
            allowed_ids.update(claim.message_ids)
        payload.append({
            "chunk_id":summary.chunk_id,
            "conversation_id":summary.conversation_id,
            "conversation_name":summary.conversation_name,
            "claims":claims,
        })
    return payload,allowed_ids

def generate_daily_brief(*, brief_date:date, messages:list[IntelligenceMessage], llm:StructuredLLM, max_chars:int=12000)->DailyBrief:
    summaries=summarize_chunks(messages,llm,max_chars=max_chars)
    payload,allowed_final_ids=_validated_claim_payload(summaries)
    merged=llm.generate_json(system=MERGE_SYSTEM,prompt=merge_prompt(json.dumps(payload,ensure_ascii=False)))
    candidates=_candidate_adapter.validate_python(merged.get("items",[]))
    by_id={m.id:m for m in messages}
    fields={name:[] for name in ("must_handle","important","actions","decisions","opportunities","risks","people_to_reply","resources","knowledge","topics")}
    for candidate in candidates:
        unvalidated=[mid for mid in candidate.message_ids if mid not in allowed_final_ids]
        if unvalidated:
            raise EvidenceError(f"final brief cited message ids not present in validated claims: {unvalidated}")
        fields[candidate.category].append(materialize_item(candidate,by_id))
    for values in fields.values():
        values.sort(key=lambda x:x.importance_score,reverse=True)
    return DailyBrief(date=brief_date,executive_summary=str(merged.get("executive_summary","")),**fields)
