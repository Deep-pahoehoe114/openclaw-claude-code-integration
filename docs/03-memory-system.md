# 记忆系统架构说明

## 背景

OpenClaw 内置了 memory-lancedb 和 memory-lancedb-pro 两个记忆插件。
本方案基于 memory-lancedb-pro，配合三个额外的 skill 构建完整的记忆生命周期管理。

---

## 记忆生命周期

```
用户对话
    ↓
autoCapture（agent_end 钩子）
每轮最多存 3 条，6 分类：
fact / preference / decision / entity / reflection / other
    ↓
LanceDB 存储
向量 + BM25 双索引
L0（摘要）/ L1（概要）/ L2（正文）三层
    ↓
autoRecall（before_agent_start 钩子）
每次注入最多 3 条相关记忆
    ↓
[每周日 03:00] memory-compaction
删除低价值 + 合并相似碎片
    ↓
[每2-4周手动] /evolve
高频模式 → AGENTS.md 永久规则
```

---

## memory-lancedb-pro 配置说明

本方案使用的配置（SiliconFlow 全家桶，全部免费 tier）：

```
embedding:  BAAI/bge-m3 (1024-dim)
reranker:   BAAI/bge-reranker-v2-m3
LLM:        DeepSeek-V3
检索模式:   hybrid (vector 70% + BM25 30%)
autoCapture: ✅
autoRecall:  ✅
smartExtraction: ✅
```

如果你使用不同的 embedding provider，memory-compaction 的相似度计算部分需要对应调整。

---

## 四阶段检索管道

memory-lancedb-pro 的检索是四个阶段串联：

**第一阶段：自适应触发**
- 强制触发：「记得」「上次」「之前」等关键词
- 跳过：问候语、肯定回复、短查询（避免无意义的检索开销）

**第二阶段：混合检索**
```
weightedFusion = vectorScore × 0.7 + BM25Score × 0.3
```

**第三阶段：Cross-Encoder 重排**
```
finalScore = rerank_score × 0.6 + original × 0.4
```

**第四阶段：Weibull 衰减**
```
Core 层：β=0.8，衰减最慢（重要记忆）
Working 层：β=1.0，标准指数衰减
Peripheral 层：β=1.3，快速淡化
```

---

## compact-guardian 与 memory-compaction 的区别

这两个 skill 解决的是不同层面的问题，经常被混淆：

| | compact-guardian | memory-compaction |
|---|---|---|
| 解决的问题 | auto-compact 失败熔断 | LanceDB 碎片堆积 |
| 触发方式 | 实时，每次 compact 失败 | 定时，每周日 03:00 |
| 操作对象 | session 压缩流程 | LanceDB 记忆条目 |
| 来源 | Claude Code 源码直接借鉴 | Claude Code autoDream 思路 |

历史上出现 226 fragments 问题的根本原因是缺少 memory-compaction。
compact-guardian 是防止问题恶化的熔断，不是解决碎片的工具。

---

## /evolve 的设计边界

/evolve 不是全自动的，这是故意的设计决策。

**为什么不自动写入：**
- 候选规则的语义需要人工判断，LLM 聚类不能保证 100% 准确
- 错误的规则写入 AGENTS.md 后会持续影响所有对话，修复成本高
- 规则膨胀是真实风险——太多规则会降低每条规则的权重

**过滤逻辑（自动排除）：**
1. 今日新建记忆（当天操作指令不纳入提炼）
2. 对话碎片（疑问/抱怨语气）
3. AGENTS.md 已有规则（相似度 ≥ 85%）
4. 已标记 `evolved: true` 的记忆

**建议的使用节奏：**
- memory-compaction 跑完后（碎片清理后质量更高）
- 积累了 1-2 个月的记忆后
- 每 2-4 周最多一次

---

## MEMORY.md 的定位

MEMORY.md 是手工维护的精华知识文件，不是 LanceDB 的替代品：

- **LanceDB**：原子化事实，自动管理，向量检索
- **MEMORY.md**：精选的项目上下文、长期偏好、重要决策

两者互补，不冲突。MEMORY.md 适合存放「每次对话都需要的背景信息」，
LanceDB 适合存放「按需检索的具体记忆」。

MEMORY.md 建议控制在 15,000 字符以内（约 4,000 tokens），
超过这个大小需要做一次整理。
