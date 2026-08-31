from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from ..raw_message import RawWechatMessage
from ..source import PollBatch, WechatMessageSource

class JsonlTailSource(WechatMessageSource):
    """Safe Server Win smoke-test backend before enabling any native WeChat adapter."""
    def __init__(self,path:str|Path): self.path=Path(path)
    def open(self)->None: self.path.parent.mkdir(parents=True,exist_ok=True); self.path.touch(exist_ok=True)
    def poll(self,checkpoint:str|None)->PollBatch:
        offset=int(checkpoint or 0); messages=[]
        with self.path.open("r",encoding="utf-8") as f:
            f.seek(offset)
            for line in f:
                if not line.strip(): continue
                item=json.loads(line)
                messages.append(RawWechatMessage(
                    external_message_id=item.get("external_message_id"),conversation_id=item["conversation_id"],
                    conversation_name=item.get("conversation_name"),sender_id=item["sender_id"],sender_name=item.get("sender_name"),
                    sent_at=datetime.fromisoformat(item["sent_at"]),message_type=item.get("message_type","text"),
                    text_content=item.get("text_content"),raw_payload=item))
            new_offset=f.tell()
        return PollBatch(messages,str(new_offset))
    def close(self)->None: pass
