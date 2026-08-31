from __future__ import annotations
import os, queue, sys, threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Any
from ..raw_message import RawWechatMessage
from ..source import PollBatch, WechatMessageSource

_TYPE_MAP={1:"text",3:"image",34:"voice",43:"video",47:"image",49:"file",10000:"system"}


def resolve_pinned_wechat_account(base_dir: str | Path, wxid_dir: str) -> tuple[str, str]:
    """Validate and resolve one exact wxid directory for a collector process."""
    base=Path(base_dir).expanduser().resolve()
    if not wxid_dir or Path(wxid_dir).name != wxid_dir:
        raise ValueError("SMI_WECHAT_WXID_DIR must be one exact wxid_* directory name")
    if not wxid_dir.startswith("wxid_"):
        raise ValueError("SMI_WECHAT_WXID_DIR must start with wxid_")
    target=base / wxid_dir
    session_db=target / "db_storage" / "session" / "session.db"
    if not session_db.exists():
        raise FileNotFoundError(f"Pinned WeChat session database not found: {session_db}")
    return target.name, str(base)


class WebotCaptureSource(WechatMessageSource):
    """Read-only adapter around webot's WcdbBackend.

    Sera does not vendor webot's native DLL or key/DRM logic. This adapter
    loads an explicitly installed webot checkout on Server Win and supplies
    a callback that always returns None, so its send path is never requested.
    """
    def __init__(self, *, webot_root:str|Path|None=None, groups:list[str]|None=None,
                 poll_seconds:float=1.0, wechat_data_dir:str|None=None,
                 wechat_wxid_dir:str|None=None, webot_env_file:str|Path|None=None,
                 backend_factory:Callable[...,Any]|None=None):
        self.webot_root=Path(webot_root).resolve() if webot_root else None
        self.groups=groups or ["*"]
        self.poll_seconds=poll_seconds
        self.wechat_data_dir=wechat_data_dir
        self.wechat_wxid_dir=wechat_wxid_dir
        self.webot_env_file=Path(webot_env_file).resolve() if webot_env_file else None
        self.backend_factory=backend_factory
        self._backend=None
        self._thread=None
        self._queue:queue.Queue[RawWechatMessage]=queue.Queue()

    def _load_factory(self):
        if self.backend_factory:
            return self.backend_factory
        if not self.webot_root or not self.webot_root.exists():
            raise FileNotFoundError("WEBOT_ROOT must point to a vetted webot checkout on Server Win")

        os.environ["WEBOT_APP_HOME"]=str(self.webot_root)
        env_file=self.webot_env_file or (self.webot_root / ".env")
        os.environ["WEBOT_ENV_FILE"]=str(env_file)
        if self.wechat_data_dir:
            os.environ["WECHAT_DATA_DIR"]=self.wechat_data_dir

        root=str(self.webot_root)
        if root not in sys.path: sys.path.insert(0,root)

        # Each multi-account collector is a separate process. If an exact
        # wxid directory is configured, replace webot's "most recent wxid"
        # selector inside this process only, before WcdbNativeClient is built.
        if self.wechat_wxid_dir:
            if not self.wechat_data_dir:
                raise ValueError("SMI_WECHAT_DATA_DIR is required when SMI_WECHAT_WXID_DIR is set")
            from src.wechat import wcdb_client as wcdb_client_module
            base_dir=self.wechat_data_dir
            wxid_dir=self.wechat_wxid_dir
            def _pinned_selector(custom_base_dir: str = ""):
                return resolve_pinned_wechat_account(custom_base_dir or base_dir, wxid_dir)
            wcdb_client_module._find_wxid_and_dbpath=_pinned_selector

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
