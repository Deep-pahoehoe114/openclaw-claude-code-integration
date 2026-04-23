# OpenClaw Enhancement & Compatibility Kit

OpenClaw Enhancement & Compatibility Kit 现在不再只是“把 Claude Code 思路移植到 OpenClaw 的 skill 仓库”，而是一个面向 OpenClaw / Claude / Codex 的治理、兼容、运行时增强层。它保留现有 `skills/` 作为内容资产，同时新增统一策略、统一上下文、统一分发、统一观测、统一适配器。

## 这个仓库现在是什么

- 一个默认本地可跑的运行时增强层
- 一个面向 OpenClaw 原生插件、Claude bundle、Codex bundle 的兼容分发层
- 一个围绕模式、权限、checks、post-edit validation 的治理层
- 一个对旧 skill 仓库友好的迁移升级层

## 核心内置能力

- `runtime core`：`WorkspaceResolver`、`SessionResolver`、`PolicyEngine`、`ContextEngine`、`MemoryProvider`、`RuleStore`、`SandboxProvider`、`TraceExporter`
- `content layer`：现有 `skills/` 全量保留
- `distribution`：从 `metadata/canonical.json` 统一生成 manifest / bundle
- `checks`：markdown 定义的检查，可在本地与 CI 共用

## 可选 Adapter

<!-- generated-adapters:start -->
- `openclaw-native`: Native OpenClaw plugin metadata and bundle output.
- `claude-bundle`: Claude-compatible bundle manifest and command roots.
- `codex-bundle`: Codex-compatible bundle manifest and hook packs.
- `lossless-context`: Optional context preservation backend for compaction workflows.
- `observability`: Structured event exporter with optional Opik/Langfuse bridges.
- `temporal-memory`: Optional temporal memory interface with local stub implementation.
- `remote-sandbox`: Optional remote sandbox provider interface.
<!-- generated-adapters:end -->

## 模式系统

- `ask`：只读、禁网、严格审批
- `plan`：规划优先，允许受控执行
- `build`：默认开发模式，允许修改和验证
- `debug`：偏诊断，保留 trace 与测试能力
- `review`：只读 review / checks
- `auto`：由 profile 与 sandbox provider 决定自动化边界

## 安装方式

### OpenClaw 原生插件

使用根目录生成的 `openclaw.plugin.json`：

```bash
python3 tools/sync_repo_state.py
cat openclaw.plugin.json
```

### Claude 兼容 Bundle

使用 `.claude-plugin/plugin.json` 和 bundle 内的 commands/settings：

```bash
python3 tools/sync_repo_state.py
cat .claude-plugin/plugin.json
```

### Codex 兼容 Bundle

使用 `.codex-plugin/plugin.json` 和 `.codex-plugin/hooks/post-edit-validation/`：

```bash
python3 tools/sync_repo_state.py
cat .codex-plugin/plugin.json
```

### 开发态安装

开发态建议直接保留源码仓库，通过 link/install 方式接入宿主。手工 `cp -r skills/*` 仍可作为兼容 fallback，但不再是主安装方案。

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

## 测试清单

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

## 目录概览

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

## 开发流程

```bash
python3 tools/sync_repo_state.py
python3 tools/run_checks.py --all
python3 tools/post_edit_validate.py
python3 tools/repo_map.py --summary
python3 tools/smoke_test.py
```

## 文档

- [架构说明](docs/ARCHITECTURE.md)
- [迁移说明](docs/MIGRATION.md)
- [审计报告](docs/AUDIT.md)
- [LLM 索引](llms.txt)
