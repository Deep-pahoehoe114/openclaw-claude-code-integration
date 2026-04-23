"""Lossless context adapter interface."""

from __future__ import annotations

import json
from pathlib import Path


class NoOpLosslessContextAdapter:
    def store(self, scope: str, payload: dict) -> dict:
        return {"stored": False, "scope": scope, "reason": "lossless context adapter disabled"}


class FileLosslessContextAdapter:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def store(self, scope: str, payload: dict) -> dict:
        target = self.root / f"{scope}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"stored": True, "scope": scope, "path": str(target)}
