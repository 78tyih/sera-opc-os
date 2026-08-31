from datetime import datetime, timezone
from pathlib import Path
import pytest
from sera_message_intelligence.collectors.wechat_local.raw_message import RawWechatMessage
from sera_message_intelligence.collectors.wechat_local.source import PollBatch, WechatMessageSource
from sera_message_intelligence.collectors.wechat_local.normalizer import normalize_wechat_message
from sera_message_intelligence.collectors.wechat_local.spool import SqliteSpool
from sera_message_intelligence.collectors.wechat_local.runner import WechatCollectorRunner
from sera_message_intelligence.collectors.wechat_local.backends.webot_capture import resolve_pinned_wechat_account

class FakeSource(WechatMessageSource):
    def open(self): pass
    def close(self): pass
    def poll(self,checkpoint):
        if checkpoint=="1": return PollBatch([], "1")
        return PollBatch([RawWechatMessage("m1","g1","Group","u1","Alice",datetime(2026,8,31,tzinfo=timezone.utc),text_content="hello")],"1")

class FakeGateway:
    def __init__(self,fail=False): self.messages=[]; self.heartbeats=[]; self.fail=fail
    def send_message(self,event):
        if self.fail: raise RuntimeError("offline")
        self.messages.append(event)
    def heartbeat(self,hb): self.heartbeats.append(hb)

def test_normalize_group():
    raw=RawWechatMessage("m1","g1","G","u1","A",datetime(2026,8,31,tzinfo=timezone.utc),text_content="x")
    event=normalize_wechat_message(raw,account_id="wx1",collector_instance_id="c1")
    assert event.platform=="wechat" and event.conversation_type=="group" and len(event.fingerprint)==64

def test_spool_dedup_and_checkpoint(tmp_path:Path):
    spool=SqliteSpool(tmp_path/"spool.db")
    raw=RawWechatMessage("m1","g1","G","u1","A",datetime(2026,8,31,tzinfo=timezone.utc),text_content="x")
    event=normalize_wechat_message(raw,account_id="wx1",collector_instance_id="c1")
    assert spool.enqueue(event) is True
    assert spool.enqueue(event) is False
    spool.set_checkpoint("9")
    assert spool.count()==1 and spool.get_checkpoint()=="9"

def test_runner_durable_before_checkpoint_and_flush(tmp_path:Path):
    spool=SqliteSpool(tmp_path/"spool.db"); gateway=FakeGateway()
    runner=WechatCollectorRunner(account_id="wx1",collector_instance_id="c1",source=FakeSource(),gateway=gateway,spool=spool,heartbeat_seconds=0)
    assert runner.run_once()==1
    assert spool.get_checkpoint()=="1"
    assert spool.count()==0
    assert len(gateway.messages)==1

def test_runner_keeps_outbox_when_gateway_offline(tmp_path:Path):
    spool=SqliteSpool(tmp_path/"spool.db"); gateway=FakeGateway(fail=True)
    runner=WechatCollectorRunner(account_id="wx1",collector_instance_id="c1",source=FakeSource(),gateway=gateway,spool=spool,heartbeat_seconds=0)
    assert runner.run_once()==1
    assert spool.get_checkpoint()=="1"
    assert spool.count()==1

def test_webot_capture_is_read_only_and_normalizes():
    from sera_message_intelligence.collectors.wechat_local.backends.webot_capture import WebotCaptureSource
    class FakeBackend:
        def __init__(self, **kwargs): self.stopped=False
        def start(self, callback):
            reply=callback({"message_id":"42","chat_id":"g@chatroom","group_name":"G","sender_id":"u","sender_name":"Alice","content":"hello","msg_type":1,"timestamp":1788134400})
            assert reply is None
        def stop(self): self.stopped=True
    source=WebotCaptureSource(backend_factory=FakeBackend,groups=["*"])
    source.open()
    import time; time.sleep(0.02)
    batch=source.poll(None)
    source.close()
    assert len(batch.messages)==1
    assert batch.messages[0].external_message_id=="42"
    assert batch.messages[0].message_type=="text"

def test_wda_source_drops_binary_media_content():
    from sera_message_intelligence.collectors.wechat_local.backends.wda_native import WdaNativeSource
    source=WdaNativeSource(wda_root="/tmp/wda",webot_env_file="/tmp/webot.env",wechat_data_dir="/tmp/wx",wechat_wxid_dir="wxid_demo")
    source._group_names={"g@chatroom":"G"}
    raw=source._to_raw("g@chatroom", {"local_id": 1, "server_id": 2, "create_time": 1788134400, "local_type": 3, "message_content": b"\\x28\\xb5\\x2f\\xfd"})
    assert raw.message_type=="image"
    assert raw.text_content is None

def test_wda_source_decodes_zstd_text_content():
    import zstandard as zstd
    from sera_message_intelligence.collectors.wechat_local.backends.wda_native import WdaNativeSource
    source=WdaNativeSource(wda_root="/tmp/wda",webot_env_file="/tmp/webot.env",wechat_data_dir="/tmp/wx",wechat_wxid_dir="wxid_demo")
    source._group_names={"g@chatroom":"G"}
    compressed=zstd.ZstdCompressor().compress("需要在周五前确认方案".encode())
    raw=source._to_raw("g@chatroom", {"local_id": 2, "server_id": 3, "create_time": 1788134400, "local_type": 1, "message_content": compressed})
    assert raw.message_type=="text"
    assert raw.text_content=="需要在周五前确认方案"

def test_wda_source_pages_active_group_window():
    from sera_message_intelligence.collectors.wechat_local.backends.wda_native import WdaNativeSource
    source=WdaNativeSource(wda_root="/tmp/wda",webot_env_file="/tmp/webot.env",wechat_data_dir="/tmp/wx",wechat_wxid_dir="wxid_demo",poll_limit=2)
    source._native=type("Native", (), {})()
    source._handle=1
    pages=[
        [{"local_id": 3, "create_time": 1000}, {"local_id": 2, "create_time": 999}],
        [{"local_id": 1, "create_time": 998}],
    ]
    source._native.get_messages=lambda _handle, _group, limit, offset: pages[0] if offset == 0 else pages[1]
    rows=source._recent_messages("g@chatroom", 998)
    assert [row["local_id"] for row in rows]==[3,2,1]

def test_exact_wxid_pin_requires_expected_session_db(tmp_path:Path):
    base=tmp_path/"xwechat_files"
    target=base/"wxid_alpha_1234"
    session=target/"db_storage"/"session"/"session.db"
    session.parent.mkdir(parents=True)
    session.write_bytes(b"db")
    wxid,resolved_base=resolve_pinned_wechat_account(base,"wxid_alpha_1234")
    assert wxid=="wxid_alpha_1234"
    assert Path(resolved_base)==base.resolve()
    with pytest.raises(FileNotFoundError):
        resolve_pinned_wechat_account(base,"wxid_missing_9999")
    with pytest.raises(ValueError):
        resolve_pinned_wechat_account(base,"..\\escape")
