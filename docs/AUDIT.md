# Audit

## 发现的问题

1. 仓库主叙述仍停留在“Claude Code skill 移植”，与当前目标“增强与兼容层”不符。
2. README、README_CN、INTEGRATION_SUMMARY、QUICKSTART 的安装方式仍以 `cp -r skills/*` 为主，和 OpenClaw 当前的插件/兼容 bundle 分发模型不一致。
3. README 标称 `8` 个 skills、`94` 个测试，但真实仓库已有 `12` 个 skills，且根测试与 skill 内测试分离，数字已经漂移。
4. `workflows/ci.yml` 放在错误目录，GitHub Actions 不会自动执行。
5. 多个脚本直接写死 `~/.openclaw/workspace`、`~/.openclaw/agents/main/sessions`、`~/.openclaw/memory/...`。
6. `yolo-permissions` 存在真实缺陷：`score_command()` 调用参数错误，导致危险 bash 命令被误判。
7. 旧实现默认绑定 LanceDB / 单 workspace / 单 provider，缺少统一策略、上下文、分发、观测、适配器抽象。

## 修复策略

1. 新增 `metadata/canonical.json` 作为单一事实源，skills、adapters、modes、distribution 元数据统一从这里读取。
2. 新增 `oeck/` 作为 runtime core 与 adapter 层，提供 `WorkspaceResolver`、`SessionResolver`、`PolicyEngine`、`ContextEngine`、`MemoryProvider`、`RuleStore`、`SandboxProvider`、`TraceExporter`。
3. 保留 `skills/` 作为 content layer，不 vendoring 第三方代码；旧脚本通过 shared config 与 resolver 兼容接入新层。
4. 新增 `tools/sync_repo_state.py`，自动生成 bundle manifests 与 README/summary 的 generated sections。
5. 新增 `.openclaw/checks/*.md`、`tools/run_checks.py`、`tools/post_edit_validate.py`，把本地检查、CI 和 post-edit validation 收口到一套机制。
6. 新增三种分发目标：`openclaw.plugin.json`、`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`，都从同一 canonical metadata 生成。
7. 新增架构、迁移、LLM 索引文档，明确核心内置能力、可选 adapter、保留兼容路径与 feature flags。
