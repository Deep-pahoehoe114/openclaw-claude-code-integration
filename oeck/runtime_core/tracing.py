"""Structured trace export."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

from .config import KitConfig
from .workspace import WorkspaceResolver


@dataclass(slots=True)
class TraceEvent:
    name: str
    payload: dict
    source: str = "oeck"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TraceExporter:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: TraceEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def create_trace_exporter(
    config: KitConfig | None = None,
    resolver: WorkspaceResolver | None = None,
) -> TraceExporter:
    resolver = resolver or WorkspaceResolver(config)
    trace_path = resolver.layout.traces_dir / "events.jsonl"
    return TraceExporter(trace_path)
