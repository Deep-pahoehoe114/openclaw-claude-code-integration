"""Workspace and path resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from .config import KitConfig, load_kit_config


@dataclass(slots=True)
class WorkspaceLayout:
    workspace_root: Path
    host_home: Path
    state_dir: Path
    skills_dir: Path
    docs_dir: Path
    metadata_dir: Path
    checks_dir: Path
    distribution_dir: Path
    sessions_state_dir: Path
    traces_dir: Path
    rules_dir: Path
    logs_dir: Path
    learnings_dir: Path
    local_rules_dir: Path
    legacy_sessions_dir: Path
    legacy_memory_dir: Path
    legacy_lancedb_dir: Path
    recovery_dir: Path


class WorkspaceResolver:
    """Central workspace resolver with legacy compatibility."""

    def __init__(self, config: KitConfig | None = None):
        self.config = config or load_kit_config()
        self.layout = WorkspaceLayout(
            workspace_root=self.config.workspace_root,
            host_home=self.config.host_home,
            state_dir=self.config.state_dir,
            skills_dir=self.config.workspace_root / "skills",
            docs_dir=self.config.workspace_root / "docs",
            metadata_dir=self.config.workspace_root / "metadata",
            checks_dir=self.config.workspace_root / ".openclaw" / "checks",
            distribution_dir=self.config.workspace_root / "dist",
            sessions_state_dir=self.config.state_dir / "sessions",
            traces_dir=self.config.state_dir / "traces",
            rules_dir=self.config.state_dir / "rules",
            logs_dir=self.config.state_dir / "logs",
            learnings_dir=self.config.state_dir / "learnings",
            local_rules_dir=self.config.state_dir / "local-rules",
            legacy_sessions_dir=self.config.host_home / "agents" / "main" / "sessions",
            legacy_memory_dir=self.config.host_home / "memory",
            legacy_lancedb_dir=self.config.host_home / "memory" / "lancedb-pro",
            recovery_dir=self.config.state_dir / "recovery",
        )

    @classmethod
    def from_workspace(cls, workspace_hint: str | Path | None = None) -> "WorkspaceResolver":
        return cls(load_kit_config(workspace_hint))

    def ensure_runtime_dirs(self) -> None:
        for path in [
            self.layout.state_dir,
            self.layout.sessions_state_dir,
            self.layout.traces_dir,
            self.layout.rules_dir,
            self.layout.logs_dir,
            self.layout.learnings_dir,
            self.layout.local_rules_dir,
            self.layout.recovery_dir,
            self.layout.checks_dir,
            self.layout.distribution_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def legacy_or_state_file(self, legacy_name: str, state_subpath: str) -> Path:
        legacy_path = self.layout.workspace_root / legacy_name
        legacy_path.parent.mkdir(parents=True, exist_ok=True)
        return legacy_path

    def log_file(self, stem: str) -> Path:
        mapping: Dict[str, str] = {
            "self-eval-reflections": ".self-eval-reflections.jsonl",
            "evolve-rule-applications": ".evolve-rule-applications.jsonl",
            "cache-monitor": ".cache-monitor.json",
            "permission-decisions": ".permission-decisions.jsonl",
            "command-execution": ".command-execution.jsonl",
            "user-interactions": ".user-interactions.jsonl",
            "fusion-decisions": ".fusion-decisions.jsonl",
            "rule-metrics": ".rule-metrics.jsonl",
            "rule-variants": ".rule-variants.jsonl",
            "ab-test-results": ".ab-test-results.jsonl",
            "optimization-log": ".optimization-log.jsonl",
            "knowledge-transfer": ".knowledge-transfer.jsonl",
            "dashboard-cache": ".dashboard-cache.json",
            "federation-log": ".federation-log.jsonl",
            "conflict-log": ".conflict-log.jsonl",
            "published-rules": ".published-rules.json",
            "rollback-log": ".rollback-log.jsonl",
        }
        legacy_name = mapping.get(stem, f".{stem}.jsonl")
        state_suffix = legacy_name.lstrip(".")
        return self.legacy_or_state_file(legacy_name, f"logs/{state_suffix}")

    def behavior_history_dir(self) -> Path:
        legacy = self.layout.workspace_root / ".behavior-analytics"
        legacy.mkdir(parents=True, exist_ok=True)
        return legacy

    def learnings_file(self) -> Path:
        legacy = self.layout.workspace_root / ".learnings" / "LEARNINGS.md"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        return legacy

    def pending_file(self) -> Path:
        legacy = self.layout.workspace_root / ".learnings" / "evolve-pending.json"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        return legacy

    def lancedb_dir(self) -> Path:
        configured = self.config.extra.get("lancedb_dir")
        if configured:
            return Path(configured).expanduser()
        workspace_candidate = self.layout.workspace_root / "memory" / "lancedb-pro"
        if workspace_candidate.exists():
            return workspace_candidate
        return self.layout.legacy_lancedb_dir

    def memory_jsonl(self) -> Path:
        workspace_candidate = self.layout.workspace_root / "memory" / "reflections.jsonl"
        if workspace_candidate.exists():
            return workspace_candidate
        self.ensure_runtime_dirs()
        return self.layout.state_dir / "memory" / "reflections.jsonl"

    def recovery_state_dir(self) -> Path:
        legacy = self.layout.workspace_root / ".recovery"
        legacy.mkdir(parents=True, exist_ok=True)
        return legacy

    def local_rules_dir(self) -> Path:
        legacy = self.layout.workspace_root / ".local-rules"
        legacy.mkdir(parents=True, exist_ok=True)
        return legacy

    def path_summary(self) -> Dict[str, str]:
        return {
            "workspace_root": str(self.layout.workspace_root),
            "state_dir": str(self.layout.state_dir),
            "checks_dir": str(self.layout.checks_dir),
            "lancedb_dir": str(self.lancedb_dir()),
            "learnings_file": str(self.learnings_file()),
            "sessions_dir": str(self.layout.legacy_sessions_dir),
        }
