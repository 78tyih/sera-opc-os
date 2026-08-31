from __future__ import annotations
import json
from typing import Protocol, Any
import httpx

class StructuredLLM(Protocol):
    def generate_json(self, *, system: str, prompt: str) -> dict[str, Any]: ...

class OpenAICompatibleLLM:
    def __init__(self, *, base_url:str, api_key:str, model:str, timeout:float=120.0):
        self.base_url=base_url.rstrip("/")
        self.api_key=api_key
        self.model=model
        self.client=httpx.Client(timeout=timeout)

    def generate_json(self, *, system:str, prompt:str)->dict[str,Any]:
        payload={"model":self.model,"messages":[{"role":"system","content":system},{"role":"user","content":prompt}],"response_format":{"type":"json_object"},"temperature":0.2}
        headers={"authorization":f"Bearer {self.api_key}","content-type":"application/json"}
        r=self.client.post(f"{self.base_url}/chat/completions",headers=headers,json=payload)
        if r.status_code == 400:
            payload.pop("response_format",None)
            r=self.client.post(f"{self.base_url}/chat/completions",headers=headers,json=payload)
        r.raise_for_status()
        content=r.json()["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content=content.split("\n",1)[1].rsplit("```",1)[0].strip()
        return json.loads(content)

    def close(self)->None: self.client.close()
