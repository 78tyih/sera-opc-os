from __future__ import annotations
import logging, time
from ...schemas import CollectorHeartbeat
from .gateway_client import MessageGatewayClient
from .normalizer import normalize_wechat_message
from .source import WechatMessageSource
from .spool import SqliteSpool

log=logging.getLogger(__name__)

class WechatCollectorRunner:
    def __init__(self, *, account_id:str, collector_instance_id:str, source:WechatMessageSource,
                 gateway:MessageGatewayClient, spool:SqliteSpool, poll_seconds:float=1.0,
                 heartbeat_seconds:float=30.0, flush_batch_size:int=100):
        self.account_id=account_id; self.collector_instance_id=collector_instance_id
        self.source=source; self.gateway=gateway; self.spool=spool
        self.poll_seconds=poll_seconds; self.heartbeat_seconds=heartbeat_seconds; self.flush_batch_size=flush_batch_size
        self.messages_received=0; self.errors=0; self.last_message_at=None
        self._last_heartbeat=0.0

    def run_once(self)->int:
        checkpoint=self.spool.get_checkpoint()
        batch=self.source.poll(checkpoint)
        enqueued=0
        for raw in batch.messages:
            event=normalize_wechat_message(raw,account_id=self.account_id,collector_instance_id=self.collector_instance_id)
            if self.spool.enqueue(event):
                enqueued+=1; self.messages_received+=1; self.last_message_at=event.sent_at
        self.spool.set_checkpoint(batch.checkpoint)
        self.flush()
        self._maybe_heartbeat()
        return enqueued

    def flush(self)->int:
        sent=0
        for row_id,event in self.spool.peek(self.flush_batch_size):
            try:
                self.gateway.send_message(event)
            except Exception as exc:
                self.errors+=1; self.spool.fail(row_id,str(exc)); break
            else:
                self.spool.ack(row_id); sent+=1
        return sent

    def _maybe_heartbeat(self,force:bool=False,status:str="online")->None:
        now=time.monotonic()
        if not force and now-self._last_heartbeat < self.heartbeat_seconds:return
        hb=CollectorHeartbeat(collector_instance_id=self.collector_instance_id,account_id=self.account_id,
            platform="wechat",status=status,last_checkpoint=self.spool.get_checkpoint(),
            last_message_at=self.last_message_at,messages_received=self.messages_received,errors=self.errors)
        try:self.gateway.heartbeat(hb)
        except Exception: self.errors+=1
        self._last_heartbeat=now

    def run_forever(self)->None:
        backoff=1.0
        self.source.open()
        try:
            self._maybe_heartbeat(force=True,status="starting")
            while True:
                try:
                    self.run_once(); backoff=1.0; time.sleep(self.poll_seconds)
                except KeyboardInterrupt: break
                except Exception:
                    self.errors+=1; log.exception("collector cycle failed")
                    self._maybe_heartbeat(force=True,status="degraded")
                    time.sleep(min(backoff,30.0)); backoff=min(backoff*2,30.0)
        finally:
            try:self._maybe_heartbeat(force=True,status="offline")
            finally:self.source.close()
