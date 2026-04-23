# OpenClaw Enhancement & Compatibility Kit

OpenClaw Enhancement & Compatibility Kit is a governance, compatibility, and runtime enhancement layer for OpenClaw, Claude, and Codex. It keeps the existing `skills/` library as content assets, but upgrades the repository into a productized runtime with unified policy, unified context, unified distribution, unified observability, and optional adapters.

## What This Repository Is

- A local-first runtime enhancement layer.
- A compatibility bridge for OpenClaw native plugins, Claude bundles, and Codex bundles.
- A governance surface for modes, permission policy, checks, and post-edit validation.
- A migration-safe wrapper around the existing skills repository.

## Core Built-ins

- `runtime core`: `WorkspaceResolver`, `SessionResolver`, `PolicyEngine`, `ContextEngine`, `MemoryProvider`, `RuleStore`, `SandboxProvider`, `TraceExporter`
- `content layer`: the existing skills remain intact under `skills/`
- `distribution`: manifests and bundle metadata are generated from `metadata/canonical.json`
- `checks`: markdown-defined validation reused locally and in CI

## Optional Adapters

<!-- generated-adapters:start -->
- `openclaw-native`: Native OpenClaw plugin metadata and bundle output.
- `claude-bundle`: Claude-compatible bundle manifest and command roots.
- `codex-bundle`: Codex-compatible bundle manifest and hook packs.
- `lossless-context`: Optional context preservation backend for compaction workflows.
- `observability`: Structured event exporter with optional Opik/Langfuse bridges.
- `temporal-memory`: Optional temporal memory interface with local stub implementation.
- `remote-sandbox`: Optional remote sandbox provider interface.
<!-- generated-adapters:end -->

## Modes

- `ask`: read-only, no network, strict approval
- `plan`: scoped planning with allowlisted execution
- `build`: default implementation mode with validation
- `debug`: diagnosis-first mode with trace support
- `review`: read-only review and checks
- `auto`: profile-driven automation with sandbox hooks

## Installation

### OpenClaw Native Plugin

Use the generated root manifest:

```bash
python3 tools/sync_repo_state.py
cat openclaw.plugin.json
```

### Claude Bundle

Use `.claude-plugin/plugin.json` and the bundled commands/settings:

```bash
python3 tools/sync_repo_state.py
cat .claude-plugin/plugin.json
```

### Codex Bundle

Use `.codex-plugin/plugin.json` and the hook pack under `.codex-plugin/hooks/post-edit-validation/`:

```bash
python3 tools/sync_repo_state.py
cat .codex-plugin/plugin.json
```

### Development Install

For local development, keep the repo checked out and link or install the appropriate manifest/bundle into your host environment. Manual `cp -r skills/*` remains possible for legacy setups, but it is no longer the primary path.

## Skills

<!-- generated-skills:start -->
- `behavior-analyzer`: Session health analysis and anomaly detection.
- `cache-monitor`: Static and dynamic prompt layer cache drift monitoring.
- `compact-guardian`: Circuit breaker and recovery flow for failed compactions.
- `evolve`: Rule extraction from reflections and learnings.
- `fusion-engine`: Multi-source context fusion for decision support.
- `knowledge-federation`: Rule sharing, federation, and long-term optimization.
- `memory-compaction`: Memory pruning, merging, and optional lossless backends.
- `rule-optimizer`: Effectiveness scoring and A/B rule refinement.
- `safe-command-execution`: AST-based shell command inspection.
- `self-eval`: Reflection capture and learnings persistence.
- `smart-compact`: Session compaction strategy and transcript rewriting.
- `yolo-permissions`: Command risk scoring and permission classification.
<!-- generated-skills:end -->

## Tests

<!-- generated-tests:start -->
- `skills/behavior-analyzer/tests/test_behavior_analyzer.py`: 10
- `skills/fusion-engine/tests/test_fusion_engine.py`: 17
- `skills/knowledge-federation/tests/test_central_api.py`: 15
- `skills/knowledge-federation/tests/test_hook_integration.py`: 10
- `skills/knowledge-federation/tests/test_knowledge_federation.py`: 29
- `skills/knowledge-federation/tests/test_long_term_evolution.py`: 17
- `skills/knowledge-federation/tests/test_rule_recommender.py`: 20
- `skills/rule-optimizer/tests/test_rule_optimizer.py`: 9
- `tests/distribution/test_sync_repo_state.py`: 1
- `tests/runtime_core/test_policy_engine.py`: 2
- `tests/runtime_core/test_validation.py`: 2
- `tests/runtime_core/test_workspace_resolver.py`: 2
- `tests/smoke/test_tools_smoke.py`: 1
- `tests/test_bash_guard.py`: 33
- `tests/test_evolve.py`: 11
- `tests/test_learnings_extractor.py`: 8
- `tests/test_permission_scorer.py`: 9
- `tests/test_recovery_manager.py`: 6
- `tests/test_self_eval.py`: 16
- `tests/test_yolo_classifier.py`: 20
- `tests/test_health_check.sh`: 1
<!-- generated-tests:end -->

## Directory Overview

<!-- generated-tree:start -->
- `metadata/`
  - `metadata/canonical.json`
- `oeck/`
  - `oeck/__init__.py`
  - `oeck/adapters`
  - `oeck/distribution`
  - `oeck/runtime_core`
- `skills/`
  - `skills/__init__.py`
  - `skills/behavior-analyzer`
  - `skills/cache-monitor`
  - `skills/compact-guardian`
  - `skills/evolve`
  - `skills/fusion-engine`
  - `skills/knowledge-federation`
  - `skills/memory-compaction`
  - `skills/rule-optimizer`
  - `skills/safe-command-execution`
  - `skills/self-eval`
  - `skills/shared`
  - `skills/smart-compact`
  - `skills/yolo-permissions`
- `docs/`
  - `docs/01-architecture.md`
  - `docs/02-prompt-engineering.md`
  - `docs/03-memory-system.md`
  - `docs/04-session-hooks.md`
  - `docs/ARCHITECTURE.md`
  - `docs/AUDIT.md`
  - `docs/MIGRATION.md`
  - `docs/generated`
- `.openclaw/`
  - `.openclaw/checks`
- `.claude-plugin/`
  - `.claude-plugin/commands`
  - `.claude-plugin/plugin.json`
  - `.claude-plugin/settings.json`
- `.codex-plugin/`
  - `.codex-plugin/hooks`
  - `.codex-plugin/plugin.json`
- `plugins/`
  - `plugins/openclaw-native`
- `tests/`
  - `tests/__init__.py`
  - `tests/conftest.py`
  - `tests/distribution`
  - `tests/runtime_core`
  - `tests/smoke`
  - `tests/test_bash_guard.py`
  - `tests/test_evolve.py`
  - `tests/test_health_check.sh`
  - `tests/test_learnings_extractor.py`
  - `tests/test_permission_scorer.py`
  - `tests/test_recovery_manager.py`
  - `tests/test_self_eval.py`
  - `tests/test_yolo_classifier.py`
- `tools/`
  - `tools/health_check.sh`
  - `tools/health_check_config.json`
  - `tools/post_edit_validate.py`
  - `tools/repo_map.py`
  - `tools/run_checks.py`
  - `tools/smoke_test.py`
  - `tools/sync_repo_state.py`
- `.github/`
  - `.github/workflows`
<!-- generated-tree:end -->

## Development Workflow

```bash
python3 tools/sync_repo_state.py
python3 tools/run_checks.py --all
python3 tools/post_edit_validate.py
python3 tools/repo_map.py --summary
python3 tools/smoke_test.py
```

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Migration](docs/MIGRATION.md)
- [Audit](docs/AUDIT.md)
- [LLM Index](llms.txt)
