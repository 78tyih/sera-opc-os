from __future__ import annotations

import logging
import os
from pathlib import Path

from sera_message_intelligence.collectors.wechat_local.backends.jsonl_tail import JsonlTailSource
from sera_message_intelligence.collectors.wechat_local.backends.webot_capture import WebotCaptureSource
from sera_message_intelligence.collectors.wechat_local.gateway_client import MessageGatewayClient
from sera_message_intelligence.collectors.wechat_local.runner import WechatCollectorRunner
from sera_message_intelligence.collectors.wechat_local.spool import SqliteSpool


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"'))


def csv(name: str, default: str = "*") -> list[str]:
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


def main() -> None:
    here = Path(__file__).resolve().parent.parent
    load_env_file(Path(os.getenv("SMI_SERVERWIN_ENV", here / "serverwin.env")))

    logging.basicConfig(level=os.getenv("SMI_LOG_LEVEL", "INFO"), format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    source_name = os.getenv("SMI_WECHAT_SOURCE", "webot_capture")
    if source_name == "jsonl":
        source = JsonlTailSource(os.getenv("SMI_JSONL_PATH", str(here / "data" / "wechat-smoke.jsonl")))
    elif source_name == "webot_capture":
        source = WebotCaptureSource(
            webot_root=os.getenv("SMI_WEBOT_ROOT"),
            webot_env_file=os.getenv("SMI_WEBOT_ENV_FILE") or None,
            groups=csv("SMI_WECHAT_GROUPS"),
            poll_seconds=float(os.getenv("SMI_POLL_SECONDS", "1.0")),
            wechat_data_dir=os.getenv("SMI_WECHAT_DATA_DIR") or None,
        )
    else:
        raise SystemExit(f"Unsupported SMI_WECHAT_SOURCE={source_name!r}")

    gateway = MessageGatewayClient(os.getenv("SMI_GATEWAY_URL", "http://127.0.0.1:8800"), api_key=os.getenv("SMI_INGEST_API_KEY") or None)
    spool = SqliteSpool(os.getenv("SMI_SPOOL_PATH", str(here / "data" / "wechat-spool.db")))

    runner = WechatCollectorRunner(
        account_id=os.environ["SMI_WECHAT_ACCOUNT_ID"],
        collector_instance_id=os.getenv("SMI_COLLECTOR_INSTANCE_ID", "serverwin-wechat-01"),
        source=source,
        gateway=gateway,
        spool=spool,
        poll_seconds=float(os.getenv("SMI_POLL_SECONDS", "1.0")),
        heartbeat_seconds=float(os.getenv("SMI_HEARTBEAT_SECONDS", "30")),
    )
    try:
        runner.run_forever()
    finally:
        gateway.close()
        spool.close()


if __name__ == "__main__":
    main()
