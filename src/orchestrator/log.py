"""Append-only event log: every state change leaves a receipt line."""
from __future__ import annotations

import json
from datetime import datetime, timezone


class EventLog:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def record(self, event: str, **fields) -> dict:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": event,
            **fields,
        }
        self.events.append(entry)
        return entry

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(e) for e in self.events)
