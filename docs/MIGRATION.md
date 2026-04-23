# Migration

## 从旧仓库定位迁移到新结构

### 定位变化

- 旧定位：`Claude Code integration skills`
- 新定位：`OpenClaw Enhancement & Compatibility Kit`

### 兼容保留

- `skills/` 目录保持不变，原脚本路径仍可用。
- `skills/shared/config.py` 现在是兼容层，底层已改为 `WorkspaceResolver`。
- 旧的 `.rule-metrics.jsonl`、`.federation-log.jsonl`、`.local-rules/` 等工作区路径仍默认保留，避免现有数据失效。

### 新增入口

- `metadata/canonical.json`
  新的单一事实源。
- `python3 tools/sync_repo_state.py`
  生成 manifests 与 README generated sections。
- `python3 tools/run_checks.py --all`
  运行统一 checks。
- `python3 tools/post_edit_validate.py`
  运行 post-edit validation。
- `python3 tools/repo_map.py --summary`
  输出 repo map / codebase summary。

### 安装方式变化

旧方式：

```bash
cp -r skills/* ~/.openclaw/workspace/skills/
```

新方式：

1. OpenClaw 原生插件：使用根目录 `openclaw.plugin.json`
2. Claude bundle：使用 `.claude-plugin/plugin.json`
3. Codex bundle：使用 `.codex-plugin/plugin.json`

开发态仍支持源码目录 link/install，但不再把手工 `cp -r skills/*` 作为主路径。

### 配置与 feature flags

- `OECK_WORKSPACE`
  覆盖 workspace 根目录。
- `OECK_STATE_DIR`
  覆盖 runtime state 目录。
- `OECK_MODE`
  选择模式 profile。
- `OECK_MEMORY_BACKEND=jsonl|lancedb|auto`
  选择内存后端。
- `OECK_FEATURE_LOSSLESS_CONTEXT=true`
  开启 lossless context adapter。
- `OECK_FEATURE_TEMPORAL_MEMORY=true`
  开启 temporal memory adapter。
- `OECK_FEATURE_REMOTE_SANDBOX=true`
  开启 remote sandbox adapter。

### 建议迁移顺序

1. 先运行 `python3 tools/sync_repo_state.py`
2. 再运行 `python3 tools/run_checks.py --all`
3. 最后按宿主选择相应 manifest / bundle 进行安装
