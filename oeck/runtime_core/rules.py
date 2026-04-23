"""Rule store abstraction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .workspace import WorkspaceResolver


class RuleStore:
    def __init__(self, resolver: WorkspaceResolver | None = None):
        self.resolver = resolver or WorkspaceResolver()
        self.rules_dir = self.resolver.local_rules_dir()
        self.rules_dir.mkdir(parents=True, exist_ok=True)

    def iter_rule_files(self) -> Iterable[Path]:
        yield from sorted(self.rules_dir.glob("*.json"))

    def list_rules(self) -> list[dict]:
        rows = []
        for path in self.iter_rule_files():
            try:
                rows.append(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue
        return rows

    def write_rule(self, rule_id: str, payload: dict) -> Path:
        target = self.rules_dir / f"{rule_id}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def rule_metrics_log(self) -> Path:
        return self.resolver.log_file("rule-metrics")
