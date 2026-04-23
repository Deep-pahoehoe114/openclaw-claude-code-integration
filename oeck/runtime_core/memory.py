"""Memory provider abstractions."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Protocol

from .config import KitConfig
from .workspace import WorkspaceResolver


@dataclass(slots=True)
class MemoryEntry:
    text: str
    category: str = "reflection"
    metadata: dict | None = None
    source: str = "local-jsonl"
    timestamp: float | None = None

    def to_json(self) -> str:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp or datetime.now(timezone.utc).timestamp()
        payload["metadata"] = self.metadata or {}
        return json.dumps(payload, ensure_ascii=False)


class MemoryProvider(Protocol):
    def iter_entries(self, category: str | None = None, limit: int | None = None) -> Iterable[MemoryEntry]:
        ...

    def append(self, entry: MemoryEntry) -> None:
        ...


class LocalJsonlMemoryProvider:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def iter_entries(self, category: str | None = None, limit: int | None = None) -> Iterable[MemoryEntry]:
        if not self.path.exists():
            return []
        rows = []
        for raw_line in self.path.read_text(encoding="utf-8").splitlines():
            if not raw_line.strip():
                continue
            try:
                payload = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            entry = MemoryEntry(
                text=payload.get("text", ""),
                category=payload.get("category", "reflection"),
                metadata=payload.get("metadata") or {},
                source=payload.get("source", "local-jsonl"),
                timestamp=payload.get("timestamp"),
            )
            if category and entry.category != category:
                continue
            rows.append(entry)
        rows.sort(key=lambda item: item.timestamp or 0, reverse=True)
        if limit is not None:
            rows = rows[:limit]
        return rows

    def append(self, entry: MemoryEntry) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(entry.to_json() + "\n")


class LanceDBMemoryProvider:
    def __init__(self, path: Path):
        self.path = path

    def _connect(self):
        import lancedb

        db = lancedb.connect(str(self.path))
        return db.open_table("memories")

    def iter_entries(self, category: str | None = None, limit: int | None = None) -> Iterable[MemoryEntry]:
        try:
            table = self._connect()
        except Exception:
            return []
        rows = []
        try:
            for row in table.scan():
                if category and row.get("category") != category:
                    continue
                rows.append(
                    MemoryEntry(
                        text=row.get("text", ""),
                        category=row.get("category", "reflection"),
                        metadata=row.get("metadata") or {},
                        source="lancedb",
                        timestamp=row.get("timestamp"),
                    )
                )
        except Exception:
            return []
        rows.sort(key=lambda item: item.timestamp or 0, reverse=True)
        if limit is not None:
            rows = rows[:limit]
        return rows

    def append(self, entry: MemoryEntry) -> None:
        table = self._connect()
        table.add(
            [
                {
                    "id": f"mem_{int((entry.timestamp or 0) * 1000)}",
                    "text": entry.text,
                    "category": entry.category,
                    "metadata": json.dumps(entry.metadata or {}, ensure_ascii=False),
                    "timestamp": entry.timestamp or datetime.now(timezone.utc).timestamp(),
                }
            ]
        )


def create_memory_provider(
    config: KitConfig | None = None,
    resolver: WorkspaceResolver | None = None,
) -> MemoryProvider:
    resolver = resolver or WorkspaceResolver(config)
    config = config or resolver.config
    if config.memory_backend == "jsonl":
        return LocalJsonlMemoryProvider(resolver.memory_jsonl())
    if config.memory_backend == "lancedb":
        return LanceDBMemoryProvider(resolver.lancedb_dir())

    lancedb_dir = resolver.lancedb_dir()
    if lancedb_dir.exists():
        try:
            return LanceDBMemoryProvider(lancedb_dir)
        except Exception:
            pass
    return LocalJsonlMemoryProvider(resolver.memory_jsonl())
