from datetime import datetime, timezone
from pathlib import Path
from sera_message_intelligence.collectors.wechat_local.raw_message import RawWechatMessage
from sera_message_intelligence.collectors.wechat_local.source import PollBatch, WechatMessageSource
from sera_message_intelligence.collectors.wechat_local.normalizer import normalize_wechat_message
from sera_message_intelligence.collectors.wechat_local.spool import SqliteSpool
from sera_message_intelligence.collectors.wechat_local.runner import WechatCollectorRunner

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
