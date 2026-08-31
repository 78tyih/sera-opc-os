from __future__ import annotations
import os, queue, sys, threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Any
from ..raw_message import RawWechatMessage
from ..source import PollBatch, WechatMessageSource

_TYPE_MAP={1:"text",3:"image",34:"voice",43:"video",47:"image",49:"file",10000:"system"}

class WebotCaptureSource(WechatMessageSource):
    """Read-only adapter around webot's WcdbBackend.

    Sera does not vendor webot's native DLL or key/DRM logic. This adapter
    loads an explicitly installed webot checkout on Server Win and supplies
    a callback that always returns None, so its send path is never requested.
    """
    def __init__(self, *, webot_root:str|Path|None=None, groups:list[str]|None=None,
                 poll_seconds:float=1.0, wechat_data_dir:str|None=None,
                 backend_factory:Callable[...,Any]|None=None):
        self.webot_root=Path(webot_root).resolve() if webot_root else None
        self.groups=groups or ["*"]
        self.poll_seconds=poll_seconds
        self.wechat_data_dir=wechat_data_dir
        self.backend_factory=backend_factory
        self._backend=None
        self._thread=None
        self._queue:queue.Queue[RawWechatMessage]=queue.Queue()

    def _load_factory(self):
        if self.backend_factory:
            return self.backend_factory
        if not self.webot_root or not self.webot_root.exists():
            raise FileNotFoundError("WEBOT_ROOT must point to a vetted webot checkout on Server Win")
        root=str(self.webot_root)
        if root not in sys.path: sys.path.insert(0,root)
        if self.wechat_data_dir:
            os.environ["WECHAT_DATA_DIR"]=self.wechat_data_dir
        from src.wechat.wcdb_backend import WcdbBackend
        return WcdbBackend

    def _on_message(self,msg:dict)->None:
        timestamp=int(msg.get("timestamp") or 0)
        sent_at=datetime.fromtimestamp(timestamp,tz=timezone.utc) if timestamp else datetime.now(timezone.utc)
        self._queue.put(RawWechatMessage(
            external_message_id=str(msg.get("message_id")) if msg.get("message_id") is not None else None,
            conversation_id=str(msg.get("chat_id") or ""),
            conversation_name=str(msg.get("group_name") or "") or None,
            sender_id=str(msg.get("sender_id") or "unknown"),
            sender_name=str(msg.get("sender_name") or "") or None,
            sent_at=sent_at,
            message_type=_TYPE_MAP.get(int(msg.get("msg_type") or 0),"unknown"),
            text_content=str(msg.get("content") or "") or None,
            raw_payload=dict(msg),
        ))
        return None

    def open(self)->None:
        factory=self._load_factory()
        self._backend=factory(bot_display_name="",groups=self.groups,poll_sec=self.poll_seconds,config=None)
        self._thread=threading.Thread(target=self._backend.start,args=(self._on_message,),name="smi-webot-capture",daemon=True)
        self._thread.start()

    def poll(self,checkpoint:str|None)->PollBatch:
        messages=[]
        while len(messages)<500:
            try: messages.append(self._queue.get_nowait())
            except queue.Empty: break
        new_checkpoint=checkpoint
        if messages and messages[-1].external_message_id:
            new_checkpoint=messages[-1].external_message_id
        return PollBatch(messages,new_checkpoint)

    def close(self)->None:
        if self._backend is not None:
            self._backend.stop()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5)
