# Architecture

## 四层结构

1. `content layer`
   现有 `skills/` 目录保留为内容资产，继续承载具体策略、压缩、权限、联邦等能力。
2. `runtime core`
   `oeck/runtime_core/` 提供统一的路径解析、模式策略、上下文收敛、内存接口、规则存储、沙箱与追踪导出。
3. `adapters`
   `oeck/adapters/` 负责 host bundle 输出与可选增强后端，包括 `openclaw-native`、`claude-bundle`、`codex-bundle`、`lossless-context`、`observability`、`temporal-memory`、`remote-sandbox`。
4. `distribution`
   `tools/sync_repo_state.py` 和 `oeck/distribution/` 从 `metadata/canonical.json` 生成 manifests、README generated sections 与 bundle metadata。

## Runtime Core

- `WorkspaceResolver`
  统一解析 workspace、state、checks、local rules、兼容日志路径。
- `SessionResolver`
  统一查找 OpenClaw / Claude / Codex transcript 目录，并提供 transcript fallback。
- `PolicyEngine`
  暴露 `ask / plan / build / debug / review / auto` 模式配置，并接入 `yolo-permissions` 风险评分。
- `ContextEngine`
  提供 repo map 和 codebase summary，用于 coding-centric 闭环。
- `MemoryProvider`
  默认自动选择本地 JSONL 或 LanceDB；未来可插入 temporal memory / graph backend。
- `RuleStore`
  统一管理本地规则文件与规则效能日志。
- `SandboxProvider`
  默认本地 provider，可替换为 remote sandbox stub。
- `TraceExporter`
  默认 JSONL 结构化事件，可升级到 observability adapter。

## 模式系统

- `ask`
  只读、禁网、严格审批。
- `plan`
  允许规划和 repo map，命令执行受限。
- `build`
  默认开发模式，允许工作区内写入和验证。
- `debug`
  偏诊断，保留 trace 与测试能力。
- `review`
  只读，适合 code review 和 checks。
- `auto`
  依赖 profile 和 sandbox provider 决定自动化边界。

## Checks 与验证闭环

- `.openclaw/checks/*.md`
  用 TOML frontmatter 定义命令与触发器。
- `tools/run_checks.py`
  统一运行 checks，本地与 CI 复用。
- `tools/post_edit_validate.py`
  post-edit validation pipeline，根据变更文件挑选 checks。
- `tools/repo_map.py`
  提供 repo map / codebase summary 能力。

## 分发

- `openclaw.plugin.json`
  OpenClaw 原生插件元数据。
- `.claude-plugin/plugin.json`
  Claude bundle 元数据，并附带 command roots 与 settings。
- `.codex-plugin/plugin.json`
  Codex bundle 元数据，并附带 hook roots。
