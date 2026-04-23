# OpenClaw 增强与兼容套件

<p align="center">
  <img src="docs/assets/oeck-github-banner.png" alt="OpenClaw 增强与兼容套件主视觉" width="100%" />
</p>

<p align="center">
  面向 OpenClaw / Claude / Codex 的治理、兼容、运行时增强层。<br/>
  把零散的 skills 仓库升级为统一策略、统一上下文、统一分发、统一观测的产品层。
</p>

<p align="center">
  <a href="README.md">简体中文</a> ·
  <a href="README_EN.md">English</a> ·
  <a href="docs/ARCHITECTURE.md">架构说明</a> ·
  <a href="docs/MIGRATION.md">迁移说明</a> ·
  <a href="docs/AUDIT.md">审计报告</a> ·
  <a href=".github/workflows/ci.yml">CI</a>
</p>

OpenClaw 增强与兼容套件（OECK）不是继续往 `skills/` 目录里堆功能，而是把这些能力放进一个可理解、可分发、可治理、可验证的运行时产品里。它默认本地可跑，同时为 OpenClaw 原生插件、Claude Bundle、Codex Bundle 提供统一产物，并为外部能力保留可选 adapter 接口。

## 这是什么

- 一个面向多宿主的增强层，不再假设只有 OpenClaw 一种运行环境。
- 一个本地优先的运行时核心，统一解析 workspace、session、memory、rule、trace。
- 一个产品化分发层，从同一份 canonical metadata 生成插件、bundle、README 清单与文档。
- 一个工程闭环层，把 checks、post-edit validation、smoke test、CI 串成同一条验证链。

## 产品亮点

<p align="center">
  <img src="docs/assets/oeck-highlights-zh.png" alt="OECK 产品亮点" width="100%" />
</p>

- `统一策略`：模式系统、审批边界、命令风险评分、规则优化不再分散在各个脚本里。
- `统一上下文`：`WorkspaceResolver`、`SessionResolver`、`MemoryProvider`、`RuleStore` 抹平旧宿主路径假设。
- `统一分发`：同一份 `metadata/canonical.json` 生成 OpenClaw、Claude、Codex 三种分发目标。
- `统一观测`：默认结构化事件导出，未来按 adapter 接 Langfuse、Opik 等系统。
- `兼容迁移`：保留现有 `skills/` 资产，并通过 shim 和 resolver 封装旧逻辑。

## 模式系统与工程闭环

<p align="center">
  <img src="docs/assets/oeck-modes-zh.png" alt="OECK 模式系统与工程闭环" width="100%" />
</p>

- `ask / plan / build / debug / review / auto` 六种模式直接定义权限、网络、执行边界。
- `yolo-permissions`、`safe-command-execution`、`rule-optimizer` 被统一接入策略引擎。
- 修改代码后，`checks`、`post-edit validation`、`smoke test`、`CI` 复用同一套校验链路。

## 三宿主分发与可选适配器

<p align="center">
  <img src="docs/assets/oeck-distribution-zh.png" alt="OECK 分发与适配器" width="100%" />
</p>

- `OpenClaw 原生插件`：根目录 `openclaw.plugin.json`
- `Claude Bundle`：`.claude-plugin/plugin.json`
- `Codex Bundle`：`.codex-plugin/plugin.json`
- `可选适配器`：`lossless-context`、`observability`、`temporal-memory`、`remote-sandbox`
- `默认原则`：本地优先、无凭证可跑、外部能力按 feature flags 与 adapter 按需开启

## 快速开始

```bash
python3 tools/generate_banner.py
python3 tools/sync_repo_state.py
python3 tools/run_checks.py --all
python3 tools/post_edit_validate.py
python3 tools/smoke_test.py
```

## 文档入口

- [English overview](README_EN.md)
- [中文别名页](README_CN.md)
- [架构说明](docs/ARCHITECTURE.md)
- [迁移说明](docs/MIGRATION.md)
- [审计报告](docs/AUDIT.md)
- [LLM 索引](llms.txt)

## 生成清单

<details>
<summary>查看内置 skills 清单</summary>

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

</details>

<details>
<summary>查看 adapters 清单</summary>

<!-- generated-adapters:start -->
- `openclaw-native`: OpenClaw 原生插件元数据与 bundle 产物。
- `claude-bundle`: Claude 兼容 bundle manifest 与命令根目录。
- `codex-bundle`: Codex 兼容 bundle manifest 与 hook 包。
- `lossless-context`: 用于压缩流程的可选上下文保真后端。
- `observability`: 结构化事件导出接口，可选接 Opik/Langfuse。
- `temporal-memory`: 可选时序记忆接口，默认提供本地 stub。
- `remote-sandbox`: 可选远程沙箱 provider 接口。
<!-- generated-adapters:end -->

</details>

<details>
<summary>查看测试清单</summary>

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

</details>

<details>
<summary>查看仓库结构概览</summary>

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

</details>
