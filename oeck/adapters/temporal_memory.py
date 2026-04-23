"""Temporal memory adapter interface."""

from __future__ import annotations

import json
from pathlib import Path


class NoOpTemporalMemoryAdapter:
    def record(self, event: dict) -> dict:
        return {"recorded": False, "reason": "temporal memory adapter disabled", "event": event}


class LocalTemporalMemoryAdapter:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: dict) -> dict:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return {"recorded": True, "path": str(self.path)}
