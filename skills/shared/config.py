#!/usr/bin/env python3
"""
config.py — 统一配置管理

所有技能共享的配置项，避免硬编码路径和魔法数字。
支持环境变量覆盖。

用法：
  from skills.shared.config import CONFIG, WORKSPACE, LANCE_DB_PATH
"""

import os
from pathlib import Path
from typing import Dict, Any


# ═══════════════════════════════════════════════════════════════════════════
# 基础路径配置
# ═══════════════════════════════════════════════════════════════════════════

# 根目录（可通过 OPENCLAW_HOME 环境变量覆盖）
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", Path.home() / ".openclaw"))

# 工作空间
WORKSPACE = OPENCLAW_HOME / "workspace"

# 记忆存储
MEMORY_DIR = OPENCLAW_HOME / "memory"
LANCE_DB_PATH = MEMORY_DIR / "lancedb-pro"

# 学习记录
LEARNINGS_DIR = WORKSPACE / ".learnings"
LEARNINGS_FILE = LEARNINGS_DIR / "LEARNINGS.md"
PENDING_FILE = LEARNINGS_DIR / "evolve-pending.json"

# Session 存储
SESSIONS_DIR = OPENCLAW_HOME / "agents" / "main" / "sessions"

# 恢复和备份
RECOVERY_DIR = WORKSPACE / ".recovery"
BACKUP_DIR = LANCE_DB_PATH / "backups"

# Skill 状态目录
SKILLS_DIR = WORKSPACE / "skills"

# ═══════════════════════════════════════════════════════════════════════════
# LanceDB 配置
# ═══════════════════════════════════════════════════════════════════════════

LANCE_DB_TABLE = "memories"

# ═══════════════════════════════════════════════════════════════════════════
# 记忆压缩配置
# ═══════════════════════════════════════════════════════════════════════════

# 删除阈值
IMPORTANCE_MIN = 0.3  # importance < 0.3 的记忆会被删除
MAX_AGE_DAYS = 14  # 14 天未检索的记忆

# 合并阈值
SIMILARITY_THRESHOLD = 0.85  # 向量相似度 >= 0.85 的记忆会合并
IMPORTANCE_THRESHOLD = 0.3  # 合并后保留的最低 importance

# 备份策略
MAX_BACKUPS = 4  # 最多保留 4 份备份
BACKUP_PREFIX = "backups"  # 备份目录前缀

# 压缩策略
COMPACT_THRESHOLD = 0.80  # token 使用率 >= 80% 时触发压缩
CONTEXT_WINDOW = 200000  # 上下文窗口大小（token）

# ═══════════════════════════════════════════════════════════════════════════
# 熔断配置
# ═══════════════════════════════════════════════════════════════════════════

MAX_FAILURES = 3  # 连续失败 >= 3 次触发熔断
CIRCUIT_TRIP_DURATION = 3600  # 熔断持续时间（秒）
CIRCUIT_STATE_FILE = "circuit_state.json"

# 指数退避重试延迟（秒）
RETRY_DELAYS = [0, 300, 1800]  # 0s, 5m, 30m

# ═══════════════════════════════════════════════════════════════════════════
# 反射/学习配置
# ═══════════════════════════════════════════════════════════════════════════

MAX_MEMORIES = 30  # 每次最多处理 30 条记忆
CATEGORY = "reflection"
REFLECTION_IMPORTANCE = 0.9  # 反射记忆的默认 importance
TOOL_FAILURE_IMPORTANCE = 0.92  # 工具失败记忆的 importance

# 规则提取
RULE_IMPORTANCE_MIN = 0.75  # 只提取 importance >= 0.75 的记忆
RULE_MAX_AGE_DAYS = 30  # 只提取 30 天内的记忆
RULE_SIMILARITY_THRESHOLD = 0.85  # 规则相似度阈值

# ═══════════════════════════════════════════════════════════════════════════
# 行为分析配置
# ═══════════════════════════════════════════════════════════════════════════

HEALTH_SCORE_WEIGHTS = {
    "error_rate": 0.40,
    "cache_hit_rate": 0.30,
    "user_satisfaction": 0.20,
    "task_completion": 0.10,
}

HEALTH_SCORE_THRESHOLDS = {
    "critical": 40,
    "warning": 70,
}

# ═══════════════════════════════════════════════════════════════════════════
# 权限评分配置
# ═══════════════════════════════════════════════════════════════════════════

PERMISSION_WEIGHTS = {
    "operation": 0.40,
    "path": 0.30,
    "context": 0.20,
    "pattern": 0.10,
}

RISK_LEVEL_THRESHOLDS = {
    "low": 30,
    "medium": 70,
}

# ═══════════════════════════════════════════════════════════════════════════
# API 配置
# ═══════════════════════════════════════════════════════════════════════════

# SiliconFlow Embedding API
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
SILICONFLOW_EMBED_URL = "https://api.siliconflow.cn/v1/embeddings"
SILICONFLOW_EMBED_MODEL = "BAAI/bge-m3"

# MiniMax API
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_EMBED_URL = "https://api.minimaxi.com/v1/embeddings"
MINIMAX_EMBED_MODEL = "minimax-embedding"
MINIMAX_CHAT_URL = "https://api.minimaxi.com/v1/chat/completions"
MINIMAX_CHAT_MODEL = "MiniMax-M2"

# Telegram 配置
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "")

# ═══════════════════════════════════════════════════════════════════════════
# 日志配置
# ═══════════════════════════════════════════════════════════════════════════

LOG_LEVEL = os.environ.get("OPENCLAW_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ═══════════════════════════════════════════════════════════════════════════
# 全局配置字典（便于序列化）
# ═══════════════════════════════════════════════════════════════════════════

CONFIG: Dict[str, Any] = {
    # 路径
    "openclaw_home": str(OPENCLAW_HOME),
    "workspace": str(WORKSPACE),
    "memory_dir": str(MEMORY_DIR),
    "lance_db_path": str(LANCE_DB_PATH),
    "learnings_dir": str(LEARNINGS_DIR),
    "sessions_dir": str(SESSIONS_DIR),
    "recovery_dir": str(RECOVERY_DIR),
    "backup_dir": str(BACKUP_DIR),

    # 阈值
    "importance_min": IMPORTANCE_MIN,
    "importance_threshold": IMPORTANCE_THRESHOLD,
    "max_age_days": MAX_AGE_DAYS,
    "max_memories": MAX_MEMORIES,
    "max_backups": MAX_BACKUPS,
    "compact_threshold": COMPACT_THRESHOLD,
    "context_window": CONTEXT_WINDOW,
    "similarity_threshold": SIMILARITY_THRESHOLD,
    "rule_similarity_threshold": RULE_SIMILARITY_THRESHOLD,

    # API
    "siliconflow_api_available": bool(SILICONFLOW_API_KEY),
    "minimax_api_available": bool(MINIMAX_API_KEY),
    "telegram_configured": bool(TG_BOT_TOKEN and TG_CHAT_ID),
}


def get_config() -> Dict[str, Any]:
    """获取完整配置字典"""
    return CONFIG.copy()


def reload_config() -> None:
    """重新加载配置（从环境变量）"""
    global OPENCLAW_HOME, WORKSPACE, LANCE_DB_PATH, LEARNINGS_DIR, LEARNINGS_FILE, PENDING_FILE
    global SESSIONS_DIR, RECOVERY_DIR, BACKUP_DIR
    global SILICONFLOW_API_KEY, MINIMAX_API_KEY, TG_BOT_TOKEN, TG_CHAT_ID, LOG_LEVEL

    OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", Path.home() / ".openclaw"))
    WORKSPACE = OPENCLAW_HOME / "workspace"
    MEMORY_DIR = OPENCLAW_HOME / "memory"
    LANCE_DB_PATH = MEMORY_DIR / "lancedb-pro"
    LEARNINGS_DIR = WORKSPACE / ".learnings"
    LEARNINGS_FILE = LEARNINGS_DIR / "LEARNINGS.md"
    PENDING_FILE = LEARNINGS_DIR / "evolve-pending.json"
    SESSIONS_DIR = OPENCLAW_HOME / "agents" / "main" / "sessions"
    RECOVERY_DIR = WORKSPACE / ".recovery"
    BACKUP_DIR = LANCE_DB_PATH / "backups"

    SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
    MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
    TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "")
    LOG_LEVEL = os.environ.get("OPENCLAW_LOG_LEVEL", "INFO").upper()
