# memory-compaction

## 用途

定期清理 LanceDB 记忆碎片，防止只进不出导致检索质量下降。

来源：Claude Code 的 autoDream 系统思路，针对 OpenClaw + LanceDB 重新实现。

---

## 安装方式

复制到 `~/.openclaw/workspace/skills/memory-compaction/SKILL.md`，
然后发给你的 OpenClaw：

```
帮我创建 memory-compaction skill 的执行脚本，并注册每周日凌晨 3 点的 cron job。
使用现有的 SiliconFlow bge-m3 做相似度计算，不引入新的 embedding provider。
```

---

## 执行逻辑

每周日 03:00 自动触发，按顺序执行：

**第一步：备份**
```
~/.openclaw/memory/lancedb-pro/backups/YYYY-MM-DD/
保留最近 4 份，更早的自动删除
```

**第二步：删除低价值记忆**
- 条件：importance < 0.3 且距上次检索超过 14 天
- 遇到任何错误：立即停止，发告警，不继续

**第三步：合并相似碎片**
- 条件：同主题下向量相似度 ≥ 0.85
- 合并策略：保留 importance 最高的那条的 L0 摘要，其余删除

**第四步：输出报告**
```
🧠 Memory Compaction 报告
删除：N 条
合并：M 簇
当前总数：X 条
耗时：Xs
```

---

## 首次使用建议

正式执行前先做 dry-run：

```
触发一次 memory-compaction 的 dry-run，只报告会删除/合并哪些，不实际执行
```

确认没有误删风险后再正式执行。

---

## 常见问题

**备份目录不存在导致失败：**
```bash
mkdir -p ~/.openclaw/memory/lancedb-pro/backups
```

**LanceDB SQL 不支持 list 类型：**
执行 update() 时需排除 vector 字段，这是 LanceDB 的已知限制。

---

## 与 compact-guardian 的关系

| skill | 解决的问题 | 触发方式 |
|---|---|---|
| compact-guardian | auto-compact 失败熔断 | 实时，每次 compact 失败时 |
| memory-compaction | LanceDB 碎片堆积 | 定时，每周日 03:00 |

两者解决不同层面的问题，都需要安装。
