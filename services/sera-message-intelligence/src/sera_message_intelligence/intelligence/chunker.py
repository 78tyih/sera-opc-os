from __future__ import annotations
from collections import defaultdict
from .schemas import IntelligenceMessage, MessageChunk

def _message_cost(m: IntelligenceMessage) -> int:
    return 80 + len(m.text_content or "")

def chunk_messages(messages: list[IntelligenceMessage], max_chars: int = 12000) -> list[MessageChunk]:
    grouped=defaultdict(list)
    for m in sorted(messages, key=lambda x:(x.platform,x.account_id,x.conversation_id,x.sent_at,x.id)):
        grouped[(m.platform,m.account_id,m.conversation_id,m.conversation_name)].append(m)
    chunks=[]
    for (platform,account_id,conversation_id,conversation_name), rows in grouped.items():
        current=[]; cost=0; index=1
        def flush():
            nonlocal current,cost,index
            if not current:return
            chunks.append(MessageChunk(chunk_id=f"{platform}:{account_id}:{conversation_id}:{index}",platform=platform,account_id=account_id,conversation_id=conversation_id,conversation_name=conversation_name,message_ids=[x.id for x in current],messages=current))
            current=[]; cost=0; index+=1
        for row in rows:
            c=_message_cost(row)
            if current and cost+c>max_chars: flush()
            current.append(row); cost+=c
        flush()
    return chunks

def format_chunk(chunk: MessageChunk) -> str:
    lines=[]
    for m in chunk.messages:
        sender=m.sender_name or m.sender_id
        content=(m.text_content or f"[{m.message_type}]").replace("\n"," ")
        lines.append(f"[m:{m.id}] [{m.sent_at.isoformat()}] {sender}: {content}")
    return "\n".join(lines)
