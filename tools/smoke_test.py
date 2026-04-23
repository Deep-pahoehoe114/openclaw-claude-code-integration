#!/usr/bin/env python3
"""Repository smoke tests for local runtime and bundle generation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oeck.distribution import build_distribution_assets, render_generated_docs
from oeck.runtime_core.context import ContextEngine
from oeck.runtime_core.policy import PolicyEngine
from oeck.runtime_core.workspace import WorkspaceResolver


def main() -> int:
    resolver = WorkspaceResolver.from_workspace(".")
    resolver.ensure_runtime_dirs()
    generated = render_generated_docs(resolver)
    manifests = build_distribution_assets(resolver)
    repo_map = ContextEngine(resolver).repo_map()
    decision = PolicyEngine(resolver.config).evaluate("bash", {"command": "pwd"}, mode="review")

    assert generated["skills_count"] >= 1
    assert "openclaw" in manifests
    assert repo_map["skills"]
    assert decision.action in {"allow", "confirm", "block"}
    print("smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
