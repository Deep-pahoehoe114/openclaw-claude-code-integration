"""Observability adapter implementations."""

from __future__ import annotations

import json
from pathlib import Path


class NoOpObservabilityAdapter:
    def emit(self, name: str, payload: dict) -> dict:
        return {"emitted": False, "name": name, "reason": "observability disabled"}


class JsonlObservabilityAdapter:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, name: str, payload: dict) -> dict:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"name": name, "payload": payload}, ensure_ascii=False) + "\n")
        return {"emitted": True, "name": name, "path": str(self.path)}


class OpikObservabilityAdapter:
    def emit(self, name: str, payload: dict) -> dict:
        return {
            "emitted": False,
            "name": name,
            "reason": "Opik adapter is a placeholder until credentials are configured",
            "payload": payload,
        }
