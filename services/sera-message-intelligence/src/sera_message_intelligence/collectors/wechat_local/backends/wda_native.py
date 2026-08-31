from __future__ import annotations

import importlib
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import zstandard as zstd
except Exception:  # pragma: no cover - optional only for non-WDA sources
    zstd = None

from ..raw_message import RawWechatMessage
from ..source import PollBatch, WechatMessageSource


_TYPE_MAP = {
    1: "text",
    3: "image",
    34: "voice",
    43: "video",
    47: "image",
    49: "file",
    10000: "system",
}
_HEX_KEY = re.compile(r"^[0-9a-fA-F]{64}$")


class WdaNativeSource(WechatMessageSource):
    """Read-only source backed by the pinned WDA native broker runtime."""

    def __init__(
        self,
        *,
        wda_root: str | Path,
        webot_env_file: str | Path,
        wechat_data_dir: str,
        wechat_wxid_dir: str,
        groups: list[str] | None = None,
        initial_window_hours: int = 8,
        poll_limit: int = 100,
    ) -> None:
        self.wda_root = Path(wda_root).expanduser().resolve()
        self.webot_env_file = Path(webot_env_file).expanduser().resolve()
        self.wechat_data_dir = Path(wechat_data_dir).expanduser().resolve()
        self.wechat_wxid_dir = wechat_wxid_dir
        self.groups = groups or ["*"]
        self.initial_window_hours = max(1, initial_window_hours)
        self.poll_limit = max(1, min(poll_limit, 4096))
        self._native: Any = None
        self._broker: Any = None
        self._handle: int | None = None
        self._group_names: dict[str, str] = {}
        self._groups: list[str] = []
        self._seen: set[str] = set()
        self._primed = False

    def _load_key(self) -> str:
        if not self.webot_env_file.is_file():
            raise FileNotFoundError(f"webot env file not found: {self.webot_env_file}")
        for line in self.webot_env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("WCDB_KEY="):
                key = line.split("=", 1)[1].strip()
                if _HEX_KEY.fullmatch(key):
                    return key
                break
        raise RuntimeError("WCDB_KEY is missing or invalid in the local webot env")

    def _load_native(self) -> Any:
        native_dir = self.wda_root / "wechat_decrypt_tool" / "native"
        if not native_dir.is_dir():
            raise FileNotFoundError(f"WDA native directory not found: {native_dir}")
        os.environ["WECHAT_TOOL_NATIVE_CORE_MODE"] = "required"
        os.environ["WCE_NATIVE_CORE_SOURCE_DIR"] = str(native_dir)
        os.environ["WECHAT_TOOL_DATA_DIR"] = str(self.wda_root / "data")
        os.environ["WECHAT_TOOL_ALLOW_REMOTE_CALLS"] = "1"
        root = str(self.wda_root)
        if root not in sys.path:
            sys.path.insert(0, root)
        return importlib.import_module("wechat_decrypt_tool.native_core_realtime")

    def open(self) -> None:
        self._native = self._load_native()
        self._broker = importlib.import_module("wechat_decrypt_tool.native_core_broker")
        self._broker._discover_database_roots = lambda: ()
        key = self._load_key()
        account_dir = self.wechat_data_dir / self.wechat_wxid_dir
        db_storage = account_dir / "db_storage"
        session_db = db_storage / "session" / "session.db"
        if not session_db.is_file():
            raise FileNotFoundError(f"pinned WeChat session database not found: {session_db}")
        self._handle = self._native.open_account(
            account=self.wechat_wxid_dir,
            native_wxid=re.sub(r"_[0-9a-fA-F]{4}$", "", self.wechat_wxid_dir),
            db_storage_dir=db_storage,
            session_db_path=session_db,
            key_hex=key,
        )
        sessions = self._native.get_sessions(self._handle)
        available = [
            str(row.get("username") or row.get("user_name") or "").strip()
            for row in sessions
            if str(row.get("username") or row.get("user_name") or "").strip().endswith("@chatroom")
        ]
        available_set = set(available)
        if len(self.groups) == 1 and self.groups[0] in {"*", "all", ""}:
            self._groups = available
        else:
            self._groups = [group for group in self.groups if group in available_set]
        if not self._groups:
            raise RuntimeError("No configured WeChat groups resolved from WCDB sessions")
        names = self._native.get_display_names(self._handle, self._groups)
        self._group_names = {group: str(names.get(group) or group) for group in self._groups}

    @staticmethod
    def _timestamp(row: dict[str, Any]) -> int:
        for key in ("create_time", "createTime"):
            try:
                value = int(row.get(key) or 0)
            except (TypeError, ValueError):
                continue
            if value > 10_000_000_000:
                value //= 1000
            if value > 0:
                return value
        return 0

    @staticmethod
    def _external_id(group: str, row: dict[str, Any]) -> str:
        server_id = str(row.get("server_id") or "").strip()
        local_id = str(row.get("local_id") or "").strip()
        created = str(row.get("create_time") or "").strip()
        return f"{group}:{server_id or local_id}:{created}"

    def _to_raw(self, group: str, row: dict[str, Any]) -> RawWechatMessage:
        timestamp = self._timestamp(row)
        sent_at = datetime.fromtimestamp(timestamp, timezone.utc) if timestamp else datetime.now(timezone.utc)
        local_type = int(row.get("local_type") or 0)
        sender = str(row.get("sender_username") or row.get("real_sender_id") or "unknown")
        content = self._decode_text(row) if local_type in {1, 10000} else None
        return RawWechatMessage(
            external_message_id=self._external_id(group, row),
            conversation_id=group,
            conversation_name=self._group_names.get(group, group),
            sender_id=sender,
            sender_name=None,
            sent_at=sent_at,
            message_type=_TYPE_MAP.get(local_type, "unknown"),
            text_content=content,
            raw_payload={
                "local_id": str(row.get("local_id") or ""),
                "server_id": str(row.get("server_id") or ""),
                "local_type": local_type,
                "create_time": timestamp,
            },
        )

    @staticmethod
    def _decode_text(row: dict[str, Any]) -> str | None:
        values = (row.get("message_content"), row.get("compress_content"))
        for value in values:
            if value is None:
                continue
            if isinstance(value, memoryview):
                value = value.tobytes()
            if isinstance(value, bytearray):
                value = bytes(value)
            if isinstance(value, bytes):
                if value.startswith(b"\x28\xb5\x2f\xfd"):
                    if zstd is None:
                        continue
                    try:
                        value = zstd.ZstdDecompressor().decompress(value)
                    except Exception:
                        continue
                try:
                    text = value.decode("utf-8", errors="strict").strip()
                except UnicodeDecodeError:
                    continue
            else:
                text = str(value).strip()
            if text and not text.startswith("b'("):
                return text
        return None

    def poll(self, checkpoint: str | None) -> PollBatch:
        if self._handle is None or self._native is None:
            raise RuntimeError("WDA native source is not open")
        now = int(time.time())
        window_hours = self.initial_window_hours if not self._primed else 1
        rows: list[RawWechatMessage] = []
        for group in self._groups:
            messages = self._recent_messages(group, now - window_hours * 3600)
            for row in messages:
                raw = self._to_raw(group, row)
                if raw.external_message_id and raw.external_message_id in self._seen:
                    continue
                if raw.external_message_id:
                    self._seen.add(raw.external_message_id)
                rows.append(raw)
        if not rows and not self._primed and self.initial_window_hours < 24:
            self.initial_window_hours = 24
            return self.poll(checkpoint)
        rows.sort(key=lambda item: item.sent_at)
        self._primed = True
        new_checkpoint = rows[-1].external_message_id if rows else checkpoint
        return PollBatch(rows, new_checkpoint)

    def _recent_messages(self, group: str, cutoff: int) -> list[dict[str, Any]]:
        """Page through newest-first messages until the time window is covered."""
        messages: list[dict[str, Any]] = []
        offset = 0
        for _ in range(100):
            page = self._native.get_messages(
                self._handle,
                group,
                limit=self.poll_limit,
                offset=offset,
            )
            if not page:
                break
            messages.extend(page)
            oldest = min((self._timestamp(row) for row in page), default=0)
            if len(page) < self.poll_limit or (oldest and oldest < cutoff):
                break
            offset += len(page)
        return [row for row in messages if self._timestamp(row) >= cutoff]

    def close(self) -> None:
        if self._native is not None and self._handle is not None:
            self._native.close_account(self._handle)
        self._handle = None
        self._native = None
        self._broker = None
