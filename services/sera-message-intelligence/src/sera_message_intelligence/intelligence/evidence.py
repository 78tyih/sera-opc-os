from __future__ import annotations
from collections import defaultdict
from .schemas import BriefItem, CandidateItem, IntelligenceMessage, SourceRef

class EvidenceError(ValueError): pass

def materialize_item(candidate: CandidateItem, messages: dict[int, IntelligenceMessage]) -> BriefItem:
    missing=[mid for mid in candidate.message_ids if mid not in messages]
    if missing:
        raise EvidenceError(f"unknown evidence message ids: {missing}")
    grouped=defaultdict(list)
    for mid in dict.fromkeys(candidate.message_ids):
        m=messages[mid]
        grouped[(m.platform,m.account_id,m.conversation_id,m.conversation_name)].append(mid)
    sources=[SourceRef(platform=k[0],account_id=k[1],conversation_id=k[2],conversation_name=k[3],message_ids=ids) for k,ids in grouped.items()]
    return BriefItem(title=candidate.title,summary=candidate.summary,importance_score=candidate.importance.score(),confidence=candidate.confidence,sources=sources)
