+++
name = "distribution-consistency"
description = "Verify generated manifests and docs stay in sync."
triggers = ["README*", "INTEGRATION_SUMMARY.md", "metadata/*", ".claude-plugin/*", ".codex-plugin/*", "plugins/*", "docs/*"]
commands = [
  "python3 tools/sync_repo_state.py --check",
  "python3 tools/smoke_test.py"
]
+++

# Distribution Consistency

Ensures bundle manifests and generated markdown sections match the canonical manifest.
