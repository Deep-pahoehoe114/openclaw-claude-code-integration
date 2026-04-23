# OpenClaw Enhancement & Compatibility Kit

<p align="center">
  <img src="docs/assets/oeck-github-banner.png" alt="OECK GitHub banner" width="100%" />
</p>

<p align="center">
  Governance, compatibility, and runtime enhancement for OpenClaw, Claude, and Codex.<br/>
  面向 OpenClaw / Claude / Codex 的治理、兼容、运行时增强层。
</p>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README_CN.md">简体中文</a> ·
  <a href="docs/ARCHITECTURE.md">Architecture</a> ·
  <a href="docs/MIGRATION.md">Migration</a> ·
  <a href="docs/AUDIT.md">Audit</a>
</p>

<p align="center">
  <a href=".github/workflows/ci.yml">CI workflow</a> ·
  <img src="https://img.shields.io/badge/hosts-OpenClaw%20%7C%20Claude%20%7C%20Codex-10202a" alt="Hosts" />
  <img src="https://img.shields.io/badge/runtime-local--first-0ea5b7" alt="Local first" />
  <img src="https://img.shields.io/badge/distribution-plugin%20%7C%20bundle%20%7C%20hooks-f38f5b" alt="Distribution targets" />
</p>

OpenClaw Enhancement & Compatibility Kit turns a loose skills collection into a coherent product surface. It keeps `skills/` as reusable content, then layers a runtime core, policy system, context system, adapters, checks, and multi-host distribution on top.

## Why OECK

- Keep OpenClaw-native workflows, but stop coupling everything to one host layout.
- Ship one canonical metadata source and generate manifests, README inventories, and bundles from it.
- Run locally by default, then enable remote sandboxing, temporal memory, and observability adapters only when needed.
- Preserve existing skills, but put them behind unified policy, unified context, unified distribution, and unified tracing.

## Host Targets

- `OpenClaw Native Plugin`: generated from [openclaw.plugin.json](openclaw.plugin.json)
- `Claude Bundle`: generated from [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- `Codex Bundle`: generated from [.codex-plugin/plugin.json](.codex-plugin/plugin.json)
- `GitHub presentation`: banner asset lives at [docs/assets/oeck-github-banner.png](docs/assets/oeck-github-banner.png)

## What You Get

- `Runtime core`: `WorkspaceResolver`, `SessionResolver`, `PolicyEngine`, `ContextEngine`, `MemoryProvider`, `RuleStore`, `SandboxProvider`, `TraceExporter`
- `Mode profiles`: `ask`, `plan`, `build`, `debug`, `review`, `auto`
- `Checks and validation`: markdown-based checks plus post-edit validation runners for local and CI reuse
- `Adapters`: OpenClaw-native, Claude bundle, Codex bundle, observability, lossless context, temporal memory, remote sandbox
- `Content layer`: the existing skills stay intact under `skills/`

## Quick Start

```bash
python3 tools/sync_repo_state.py
python3 tools/run_checks.py --all
python3 tools/post_edit_validate.py
python3 tools/smoke_test.py
```

The repository is local-first by default. Optional external integrations stay behind adapter interfaces and feature flags, so a clean checkout still runs without cloud credentials.

## Built-In vs Optional

- Built in: runtime core, mode profiles, plugin and bundle generation, checks runner, post-edit validation, repo map, smoke tests
- Optional by adapter: Opik or future Langfuse exporters, temporal memory backends, remote sandboxes, lossless context backends
- Migration friendly: legacy `skills/` entrypoints remain available through resolver-backed compatibility shims

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

## Adapters

<!-- generated-adapters:start -->
- `openclaw-native`: Native OpenClaw plugin metadata and bundle output.
- `claude-bundle`: Claude-compatible bundle manifest and command roots.
- `codex-bundle`: Codex-compatible bundle manifest and hook packs.
- `lossless-context`: Optional context preservation backend for compaction workflows.
- `observability`: Structured event exporter with optional Opik/Langfuse bridges.
- `temporal-memory`: Optional temporal memory interface with local stub implementation.
- `remote-sandbox`: Optional remote sandbox provider interface.
<!-- generated-adapters:end -->

## Test Inventory

<!-- generated-tests:start -->
- `skills/behavior-analyzer/tests/test_behavior_analyzer.py`: 10
- `skills/fusion-engine/tests/test_fusion_engine.py`: 17
- `skills/knowledge-federation/tests/test_central_api.py`: 15
- `skills/knowledge-federation/tests/test_hook_integration.py`: 10
- `skills/knowledge-federation/tests/test_knowledge_federation.py`: 29
- `skills/knowledge-federation/tests/test_long_term_evolution.py`: 17
- `skills/knowledge-federation/tests/test_rule_recommender.py`: 20
- `skills/rule-optimizer/tests/test_rule_optimizer.py`: 9
- `tests/distribution/test_sync_repo_state.py`: 2
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

## Repository Layout

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
  - `docs/assets`
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
  - `tools/generate_banner.py`
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

## Maintainer Workflow

```bash
python3 tools/sync_repo_state.py
python3 tools/run_checks.py --all
python3 tools/post_edit_validate.py metadata/canonical.json README.md
python3 tools/repo_map.py --summary
python3 tools/smoke_test.py
```

## Documentation

- [Chinese overview](README_CN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Migration](docs/MIGRATION.md)
- [Audit](docs/AUDIT.md)
- [LLM index](llms.txt)
