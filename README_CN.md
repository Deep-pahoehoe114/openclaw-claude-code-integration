# OpenClaw Enhancement & Compatibility Kit

<p align="center">
  <img src="docs/assets/oeck-github-banner.png" alt="OECK GitHub 横幅" width="100%" />
</p>

<p align="center">
  面向 OpenClaw / Claude / Codex 的治理、兼容、运行时增强层。<br/>
  Governance, compatibility, and runtime enhancement for OpenClaw, Claude, and Codex.
</p>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README_CN.md">简体中文</a> ·
  <a href="docs/ARCHITECTURE.md">架构说明</a> ·
  <a href="docs/MIGRATION.md">迁移说明</a> ·
  <a href="docs/AUDIT.md">审计报告</a>
</p>

<p align="center">
  <a href=".github/workflows/ci.yml">CI workflow</a> ·
  <img src="https://img.shields.io/badge/hosts-OpenClaw%20%7C%20Claude%20%7C%20Codex-10202a" alt="Hosts" />
  <img src="https://img.shields.io/badge/runtime-local--first-0ea5b7" alt="Local first" />
  <img src="https://img.shields.io/badge/distribution-plugin%20%7C%20bundle%20%7C%20hooks-f38f5b" alt="Distribution targets" />
</p>

OpenClaw Enhancement & Compatibility Kit 不再只是零散 skills 的集合，而是一个产品化的增强层。它保留 `skills/` 作为内容资产，再往上叠加运行时核心、策略系统、上下文系统、适配器、检查机制，以及面向多个宿主的分发能力。

## 为什么是 OECK

- 保留 OpenClaw 原生工作流，但不再把能力绑死在单一宿主目录结构上。
- 以一份 canonical metadata 为事实源，统一生成 manifest、README 清单和 bundle。
- 默认本地可运行，远程沙箱、时序记忆、可观测性等能力按 adapter 按需开启。
- 现有 skills 继续可用，但统一纳入策略、上下文、分发和追踪体系。

## 支持的宿主目标

- `OpenClaw 原生插件`：由 [openclaw.plugin.json](openclaw.plugin.json) 生成
- `Claude Bundle`：由 [.claude-plugin/plugin.json](.claude-plugin/plugin.json) 生成
- `Codex Bundle`：由 [.codex-plugin/plugin.json](.codex-plugin/plugin.json) 生成
- `GitHub 展示素材`：横幅文件在 [docs/assets/oeck-github-banner.png](docs/assets/oeck-github-banner.png)

## 你会得到什么

- `运行时核心`：`WorkspaceResolver`、`SessionResolver`、`PolicyEngine`、`ContextEngine`、`MemoryProvider`、`RuleStore`、`SandboxProvider`、`TraceExporter`
- `模式系统`：`ask`、`plan`、`build`、`debug`、`review`、`auto`
- `检查与验证`：基于 markdown 的 checks，以及本地和 CI 复用的 post-edit validation
- `适配器层`：OpenClaw 原生、Claude bundle、Codex bundle、observability、lossless context、temporal memory、remote sandbox
- `内容层`：现有技能完整保留在 `skills/`

## 快速开始

```bash
python3 tools/sync_repo_state.py
python3 tools/run_checks.py --all
python3 tools/post_edit_validate.py
python3 tools/smoke_test.py
```

仓库默认走本地优先模式。外部集成全部通过 adapter 接口和 feature flags 接入，所以干净 checkout 不需要云端凭证也能直接运行。

## 内置能力与可选能力

- 内置：runtime core、模式 profile、插件和 bundle 生成、checks runner、post-edit validation、repo map、smoke tests
- 可选：Opik 或未来 Langfuse 导出器、时序记忆后端、远程沙箱、lossless context 后端
- 迁移友好：旧 `skills/` 入口仍通过 resolver-backed shim 保持兼容

## Skills

<!-- generated-skills:start -->
- `behavior-analyzer`: 会话健康分析与异常检测。
- `cache-monitor`: 静态与动态提示层缓存漂移监控。
- `compact-guardian`: 面向压缩失败场景的熔断与恢复流程。
- `evolve`: 从反思与学习记录中提炼规则。
- `fusion-engine`: 面向决策支持的多源上下文融合。
- `knowledge-federation`: 规则共享、联邦协同与长期优化。
- `memory-compaction`: 记忆裁剪、合并与可选无损后端。
- `rule-optimizer`: 规则效果评分与 A/B 精炼。
- `safe-command-execution`: 基于 AST 的 shell 命令安全检查。
- `self-eval`: 反思采集与学习沉淀。
- `smart-compact`: 会话压缩策略与转录重写。
- `yolo-permissions`: 命令风险评分与权限分类。
<!-- generated-skills:end -->

## Adapters

<!-- generated-adapters:start -->
- `openclaw-native`: OpenClaw 原生插件元数据与 bundle 产物。
- `claude-bundle`: Claude 兼容 bundle manifest 与命令根目录。
- `codex-bundle`: Codex 兼容 bundle manifest 与 hook 包。
- `lossless-context`: 用于压缩流程的可选上下文保真后端。
- `observability`: 结构化事件导出接口，可选接 Opik/Langfuse。
- `temporal-memory`: 可选时序记忆接口，默认提供本地 stub。
- `remote-sandbox`: 可选远程沙箱 provider 接口。
<!-- generated-adapters:end -->

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

## 仓库结构

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

## 维护流程

```bash
python3 tools/sync_repo_state.py
python3 tools/run_checks.py --all
python3 tools/post_edit_validate.py metadata/canonical.json README.md README_CN.md
python3 tools/repo_map.py --summary
python3 tools/smoke_test.py
```

## 文档入口

- [English overview](README.md)
- [架构说明](docs/ARCHITECTURE.md)
- [迁移说明](docs/MIGRATION.md)
- [审计报告](docs/AUDIT.md)
- [LLM 索引](llms.txt)
