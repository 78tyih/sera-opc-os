from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from .raw_message import RawWechatMessage

@dataclass(slots=True)
class PollBatch:
    messages: list[RawWechatMessage]
    checkpoint: str | None

class WechatMessageSource(ABC):
    """Read-only source contract. Implementations must never send WeChat messages."""
    @abstractmethod
    def open(self) -> None: ...
    @abstractmethod
    def poll(self, checkpoint: str | None) -> PollBatch: ...
    @abstractmethod
    def close(self) -> None: ...
