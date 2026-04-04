# OpenClaw × Claude Code 精华整合

> 把 Claude Code 源码里最有价值的工程实践，移植到 OpenClaw 个人 AI 助手。
>
> self-eval · evolve · 记忆压缩 · 权限分类 · Bash 安全层 · session hooks

---

## 故事：从一次源码泄露开始的工程整合

**2026 年 3 月 31 日**，Claude Code 的完整 TypeScript 源码意外泄露。源码揭示了一套生产级 AI Agent 的核心工程系统——这些东西从未出现在官方文档里：

| 系统 | 作用 |
|------|------|
| **autoDream** | 24h+5sessions 自动整合记忆 |
| **KAIROS** | 始终在线的主动感知循环 |
| **YOLO 分类器** | Bash 命令四级风险评估，fail-closed |
| **压缩熔断机制** | 防止 auto-compact 死循环 |
| **四层 Bash 安全** | AST 解析 → 正则验证 → 权限规则 → OS 沙箱 |

这套系统的背后是 **$2.5B ARR 商业产品**在真实生产环境里踩过的坑。

**本仓库**把其中对 OpenClaw 用户真正有价值的部分提炼出来，整理成可直接使用的 skill 和配置——不需要理解源码，直接安装使用。

---

## 你得到了什么

### 🔧 8 个可安装的 Skills

| Skill | 功能 | 触发方式 |
|-------|------|---------|
| **self-eval** | 每次 session 结束检测异常，写入 reflection 记忆 | `command:stop` hook |
| **evolve** | 从 reflection 记忆提炼 NEVER/MUST 规则 | 手动或 `gateway:startup` |
| **memory-compaction** | 每周自动整理 LanceDB，删除低价值记忆 + 合并相似碎片 | cron（每周日凌晨3点） |
| **compact-guardian** | 压缩连续3次失败后熔断，停用自动压缩 + Telegram 告警 | 自动监控 |
| **cache-monitor** | agent:bootstrap 时检测 prompt cache 是否失效 | `agent:bootstrap` hook |
| **smart-compact** | LLM 摘要压缩 session 文件 | 手动 |
| **yolo-permissions** | 三级权限分类（LOW/MEDIUM/HIGH），fail-closed | 自动集成到 exec |
| **safe-command-execution** | Bash AST 解析 + 正则验证，检测危险命令 | 自动集成到 exec |

### 📜 配置示例

- `SOUL.md` — 人格与表达规范（含 Akino 规则）
- `AGENTS.md` — 完整行为协议（含 11 条用户纠正检测规则）
- `docs/` — 4 篇设计文档，解释背后的工程思路

### 🧪 测试套件

94 个 pytest 测试，覆盖 bash_guard / self_eval / evolve / yolo_classifier

---

## 与 Claude Code 原文的对比

| 维度 | Claude Code 源码 | 本整合方案 | 状态 |
|------|-----------------|-----------|------|
| autoDream | ✅ 24h+5sessions 自动整合 | ❌ 需 OpenClaw 支持 `session:end` 钩子 | [已向官方提 issue](https://github.com/openclaw/openclaw/issues/60514) |
| YOLO Bash 分类 | ✅ 四级风险，fail-closed | ✅ 已实现 | ✅ 可用 |
| 四层 Bash 安全 | ✅ AST+正则+权限+沙箱 | ✅ AST+正则已实现，沙箱需 bwrap | ⚠️ 部分 |
| 工具失败协议 | ✅ 明确处理路径 | ✅ 写入 AGENTS.md | ✅ 可用 |
| 压缩熔断 | ✅ auto-compact 死循环保护 | ✅ 已实现 | ✅ 可用 |
| 记忆三层架构 | ✅ LanceDB 自动整合 | ✅ 已有脚本支撑 | ✅ 可用 |
| evolve 规则提炼 | ❌ 无 | ✅ 手动触发 | ✅ 可用 |
| Fork cache 复用 | ✅ 子 agent 复用 prompt cache | ❌ MiniMax 不支持 | ❌ 不可行 |

---

## 系统架构

```
用户对话
    │
    ├── command:stop ──→ self_eval.py ──→ LanceDB (reflection)
    │
    ├── agent:bootstrap ──→ cache_monitor.py ──→ 静态层变更检测
    │
    └── gateway:startup ──→ evolve 提醒 ──→ 手动触发规则提炼

─────────────────────────────────────────────────

LanceDB memories 表
    │
    ├── 实时：autoCapture（memory-lancedb-pro 插件）
    │
    ├── 每周 cron ──→ memory_compaction.py ──→ 备份 + 删除 + 合并
    │
    └── 手动 evolve ──→ 规则写入 AGENTS.md
```

---

## 快速安装

### 第一步：安装插件

```bash
# 克隆仓库
git clone https://github.com/ybbms777/openclaw-claude-code-integration.git
cd openclaw-claude-code-integration

# 安装所有 skills
cp -r skills/* ~/.openclaw/workspace/skills/

# 注册 hooks（自动集成到 OpenClaw）
openclaw hooks enable self-eval-hook
openclaw hooks enable cache-monitor-hook
openclaw hooks enable evolve-hook

# 重启 Gateway
openclaw gateway restart
```

### 第二步：复制配置文件

```bash
cp SOUL.md ~/.openclaw/workspace/SOUL.md
cp AGENTS.md ~/.openclaw/workspace/AGENTS.md
```

按你的实际情况修改 `SOUL.md` 第二章的中文表达规范，以及 `AGENTS.md` 里的个人信息规则。

### 第三步：确认生效

```bash
openclaw skills list | grep -E "self-eval|evolve|compact|cache|yolo|safe"
```

看到 8 个 skills 都列出来即安装成功。

---

## 核心设计思路

### 提示词即协议（Prompt-as-Protocol）

Claude Code 最重要的工程哲学：**不要写模糊指令，只写明确协议。**

```markdown
# ❌ 模糊指令（无效）
尽量小心处理涉及资金或外部发送的操作

# ✅ 明确协议（可执行）
NEVER 直接修改涉及资金/仓位/外部发送的操作，必须先生成变更计划等用户确认
```

规则分类：
- `NEVER` — 禁止行为（不可绕过）
- `MUST` — 必须执行
- `ALWAYS` — 每次都要做

### 静态/动态分层（Prompt Cache 优化）

```
┌─────────────────────────────────────┐
│  静态层（每次对话不变化，命中 cache） │
│  SOUL.md / AGENTS.md / TOOLS.md    │
│  USER.md / IDENTITY.md              │
│  HEARTBEAT.md                      │
├────────── <!-- DYNAMIC_BOUNDARY --> ─┤
│  动态层（每次刷新，按需注入）        │
│  MEMORY.md                         │
│  LanceDB 检索结果                   │
│  当前对话上下文                     │
└─────────────────────────────────────┘
```

在 HEARTBEAT.md 和 MEMORY.md 之间插入 `<!-- DYNAMIC_BOUNDARY -->` 分隔符，边界前的内容稳定命中 prompt cache，每次对话节省约 6,000-8,000 tokens。

### 支持 Prompt Cache 的模型

| 模型 | 缓存机制 | 配置方式 | 备注 |
|------|---------|---------|------|
| **Claude**（Anthropic API） | 原生自动缓存 | 无需配置 | Claude Code 专用，缓存最完善 |
| **GPT-4o**（OpenAI API） | 自动缓存 | 无需配置 | 超过 1024 tokens 自动生效 |
| **Gemini 1.5 Pro**（Google API） | 显式 Context Caching | 需手动创建缓存对象 | 需要预先创建缓存 |
| **DeepSeek V3/R1**（SiliconFlow） | 支持 | SiliconFlow 上已配置 | MiniMax 暂不支持 |

> **当前 OpenClaw（MiniMax）**：不支持 prompt cache 的自动复用，因为 MiniMax API 不暴露 cache token 机制。但静态/动态分层架构已就绪，模型支持后自动生效。

### 工具调用失败协议

```markdown
任何工具调用失败时：
1. 先用 memory_recall 搜索相关关键词
2. 最多重试 2 次，每次改变策略
3. 2 次后仍失败：停止，报告原因，等待指示
4. NEVER 自动切换其他工具绕过问题
5. 高风险工具失败：立即停止，发 Telegram 告警
```

没有这个协议，agent 在工具卡住时会一直重试直到 token 耗尽。

### 记忆三层架构

```
对话记录
    ↓ autoCapture（每轮最多3条）
LanceDB 原子记忆（实时写入）
    ↓ memory_compaction（每周整理）
高质量记忆条目（删除+合并）
    ↓ /evolve（手动触发）
AGENTS.md 永久规则（行为改变）
```

三层对应三个时间尺度：实时、周级、月级。缺少任何一层都会导致记忆系统退化。

---

## 目录结构

```
openclaw-claude-code-integration/
├── README.md                          # 本文件
├── README_EN.md                       # English version
├── SOUL.md                            # 人格与表达规范示例
├── AGENTS.md                          # 完整行为协议（含11条规则）
├── MANUAL.md                          # 使用手册
├── SKILL.md                           # Skill 开发规范
├── skills/
│   ├── self-eval/                    # 自我评估脚本
│   │   └── scripts/self_eval.py
│   ├── evolve/                       # 规则提炼
│   │   └── scripts/evolve.py
│   ├── memory-compaction/             # LanceDB 定期整理
│   │   └── scripts/memory_compaction.py
│   ├── compact-guardian/              # 压缩熔断
│   │   └── scripts/compact_guardian.py
│   ├── cache-monitor/                # Prompt cache 监控
│   │   └── scripts/cache_monitor.py
│   ├── smart-compact/                 # LLM 摘要压缩
│   │   └── scripts/smart_compact.py
│   ├── yolo-permissions/              # 三级权限分类
│   │   └── scripts/yolo_classifier.py
│   │   └── scripts/bash_guard.py
│   └── safe-command-execution/        # Bash AST 安全层
│       └── scripts/safe_ast_check.py
│       └── skills/bash_ast/           # AST 解析子模块
├── tests/                            # pytest 测试套件（94测试）
│   ├── test_bash_guard.py
│   ├── test_self_eval.py
│   ├── test_evolve.py
│   └── test_yolo_classifier.py
└── docs/
    ├── 01-architecture.md            # 设计思路详解
    ├── 02-prompt-engineering.md       # 提示词工程对比分析
    ├── 03-memory-system.md            # 记忆系统架构
    └── 04-session-hooks.md            # 钩子注册说明
```

---

## 适用对象

- **OpenClaw 重度用户**：文件直接复制使用，按说明调整个人信息
- **AI Agent 开发者**：设计思路和提示词架构可移植到其他框架
- **对 AI 工程化感兴趣**：从商业产品（$2.5B ARR）源码提取的实战经验

---

## 已知限制

1. **`session:end` 钩子**：OpenClaw 当前版本不支持，已向[官方提 issue](https://github.com/openclaw/openclaw/issues/60514)。目前用 `command:stop` 近似替代，session 超时/断连时不触发。
2. **Fork cache 复用**：Claude Code 支持子 agent 复用父 prompt cache，MiniMax 不支持此特性。
3. **OS 沙箱层**：Bash AST 安全层只实现了 AST 解析+正则验证，Linux namespace/bwrap 沙箱需要系统级支持。

---

## ⚠️ 免责声明

本仓库**不包含任何 Claude Code 原始源码**，只提取了工程思路和设计模式。Claude Code 源码版权属于 Anthropic PBC。

---

## 致谢

- Claude Code 源码发现者：Chaofan Shou（[@Fried_rice](https://twitter.com/Fried_rice)）
- OpenClaw 项目：Peter Steinberger（[@steipete](https://twitter.com/steipete)）
- Compound Engineering 插件：EveryInc（[@EveryInc](https://github.com/EveryInc)）

---

## License

MIT — 配置文件和 skill 模板可自由使用和修改。
