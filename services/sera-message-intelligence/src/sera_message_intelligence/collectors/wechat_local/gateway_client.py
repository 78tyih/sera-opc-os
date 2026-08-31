from __future__ import annotations
import httpx
from ...schemas import CollectorHeartbeat, MessageEventV1

class MessageGatewayClient:
    def __init__(self, base_url:str, api_key:str|None=None, timeout:float=10.0):
        self.base_url=base_url.rstrip("/")
        self.headers={"x-smi-api-key":api_key} if api_key else {}
        self.client=httpx.Client(timeout=timeout, headers=self.headers)

    def send_message(self,event:MessageEventV1)->None:
        r=self.client.post(f"{self.base_url}/v1/messages",content=event.model_dump_json(),headers={"content-type":"application/json"})
        if r.status_code not in (200,201):
            r.raise_for_status()

    def heartbeat(self,hb:CollectorHeartbeat)->None:
        r=self.client.post(f"{self.base_url}/v1/collectors/heartbeat",content=hb.model_dump_json(),headers={"content-type":"application/json"})
        r.raise_for_status()

    def close(self)->None:
        self.client.close()
