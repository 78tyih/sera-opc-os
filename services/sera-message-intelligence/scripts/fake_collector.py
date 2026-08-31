import argparse
from datetime import datetime, timezone

import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/v1/messages")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()
    payload = {
        "schema_version": "1.0",
        "platform": "fake",
        "account_id": "demo-account",
        "collector_instance_id": "fake-collector-01",
        "external_message_id": "demo-message-001",
        "conversation_id": "demo-group",
        "conversation_type": "group",
        "conversation_name": "Demo Group",
        "sender_id": "user-001",
        "sender_name": "Demo User",
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "message_type": "text",
        "text_content": "Sera Message Intelligence P0 ingest smoke test.",
        "raw_payload": {"source": "fake_collector"},
    }
    headers = {"X-SMI-API-Key": args.api_key} if args.api_key else {}
    response = httpx.post(args.url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
