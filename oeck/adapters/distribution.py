"""Distribution adapters for host bundles."""

from __future__ import annotations

import json
from pathlib import Path

from oeck.runtime_core.workspace import WorkspaceResolver


class _BaseDistributionAdapter:
    def __init__(self, resolver: WorkspaceResolver | None = None):
        self.resolver = resolver or WorkspaceResolver()
        self.metadata = json.loads((self.resolver.layout.metadata_dir / "canonical.json").read_text(encoding="utf-8"))

    def skill_roots(self) -> list[str]:
        return [item["path"] for item in self.metadata["skills"]]


class OpenClawNativeAdapter(_BaseDistributionAdapter):
    def build_manifest(self) -> dict:
        return {
            "schemaVersion": 1,
            "id": self.metadata["kit"]["id"],
            "name": self.metadata["kit"]["name"],
            "version": self.metadata["kit"]["version"],
            "description": self.metadata["kit"]["tagline"],
            "skills": self.skill_roots(),
            "checks": [".openclaw/checks"],
            "entry": self.metadata["distribution"]["openclaw_plugin"]["entry"],
        }


class ClaudeBundleAdapter(_BaseDistributionAdapter):
    def build_manifest(self) -> dict:
        return {
            "id": self.metadata["kit"]["id"],
            "name": self.metadata["kit"]["name"],
            "version": self.metadata["kit"]["version"],
            "description": self.metadata["kit"]["tagline"],
            "skillRoots": self.skill_roots(),
            "commandRoots": [".claude-plugin/commands"],
            "settingsPath": ".claude-plugin/settings.json",
            "checks": [".openclaw/checks"],
        }


class CodexBundleAdapter(_BaseDistributionAdapter):
    def build_manifest(self) -> dict:
        return {
            "id": self.metadata["kit"]["id"],
            "name": self.metadata["kit"]["name"],
            "version": self.metadata["kit"]["version"],
            "description": self.metadata["kit"]["tagline"],
            "skillRoots": self.skill_roots(),
            "hookRoots": [".codex-plugin/hooks"],
            "checks": [".openclaw/checks"],
        }
