"""Policy engine and mode profiles."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .config import KitConfig, load_kit_config
from .sandbox import create_sandbox_provider
from .workspace import WorkspaceResolver


@dataclass(slots=True)
class PolicyDecision:
    mode: str
    risk: str
    action: str
    reasons: list[str] = field(default_factory=list)
    score: float | None = None
    metadata: dict = field(default_factory=dict)


class PolicyEngine:
    def __init__(self, config: KitConfig | None = None):
        self.config = config or load_kit_config()
        self.resolver = WorkspaceResolver(self.config)
        self.sandbox = create_sandbox_provider(self.config)
        manifest = Path(self.resolver.layout.metadata_dir / "canonical.json")
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        self.mode_profiles = {item["id"]: item for item in payload["modes"]}

    def profiles(self) -> dict:
        return self.mode_profiles

    def evaluate(self, tool_name: str, params: dict | None = None, mode: str | None = None) -> PolicyDecision:
        params = params or {}
        active_mode = mode or self.config.mode
        profile = self.mode_profiles.get(active_mode, self.mode_profiles["build"])
        reasons: list[str] = []
        score = None
        risk = "LOW"
        action = "allow"

        command = params.get("command", "")
        if tool_name == "bash":
            score, risk, action = self._score_bash(command, active_mode)
            reasons.append(f"bash risk scored via yolo-permissions: {risk}")
        elif tool_name in {"write", "edit"}:
            risk = "MEDIUM"
            action = "confirm"
            reasons.append("write/edit operations require confirmation in policy engine")

        sandbox_decision = self.sandbox.evaluate(command, active_mode)
        if not sandbox_decision.allowed:
            action = "block"
            risk = "HIGH"
            reasons.append(sandbox_decision.reason)

        if profile["approval"] == "strict" and action != "allow":
            reasons.append("mode profile enforces strict approval")

        return PolicyDecision(
            mode=active_mode,
            risk=risk,
            action=action,
            reasons=reasons,
            score=score,
            metadata={"profile": profile},
        )

    def _score_bash(self, command: str, mode: str) -> tuple[float, str, str]:
        try:
            from skills.yolo_permissions.scripts.permission_scorer import PermissionScorer
        except ImportError:
            import importlib

            scorer_module = importlib.import_module("skills.yolo-permissions.scripts.permission_scorer")
            PermissionScorer = scorer_module.PermissionScorer

        scorer = PermissionScorer()
        score = scorer.score_command("bash", {"command": command}, context={"mode": mode})
        risk, _ = scorer.risk_level(score)
        action = "allow" if risk == "LOW" else "confirm"
        if risk == "HIGH":
            action = "block" if mode in {"ask", "review"} else "confirm"
        return score, risk, action
