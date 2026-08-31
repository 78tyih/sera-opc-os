from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from .schemas import CollectorHeartbeat, MessageEventV1


class Collector(ABC):
    """Platform adapter contract. Core code must never import platform-native SDKs."""

    @property
    @abstractmethod
    def collector_instance_id(self) -> str: ...

    @property
    @abstractmethod
    def platform(self) -> str: ...

    @abstractmethod
    def poll(self) -> Iterable[MessageEventV1]: ...

    @abstractmethod
    def checkpoint(self) -> str | None: ...

    @abstractmethod
    def heartbeat(self) -> CollectorHeartbeat: ...
