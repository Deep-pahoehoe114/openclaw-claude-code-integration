#!/bin/bash
##############################################################################
# health_check.sh — OpenClaw 系统健康检查仪表板
#
# 功能：
#   1. 检查 MEMORY.md 容量
#   2. 检查 memory-compaction 上次运行时间
#   3. 检查 compact-guardian 熔断状态
#   4. 统计 AGENTS.md 规则数
#   5. 统计最近 7 天 session 数
#   6. 检查 LanceDB memories 表大小
#   7. 报告最近的脚本错误
#   8. 输出彩色 terminal 仪表板
#
# 用法：
#   bash health_check.sh                  # 完整检查
#   bash health_check.sh --json          # JSON 输出
#   bash health_check.sh --html          # HTML 输出
#
##############################################################################

set -euo pipefail

# ─── 配置 ─────────────────────────────────────────────────────────────────

WORKSPACE="${HOME}/.openclaw/workspace"
LANCEDB_PATH="${HOME}/.openclaw/memory/lancedb-pro"
MEMORY_FILE="${WORKSPACE}/MEMORY.md"
AGENTS_FILE="${WORKSPACE}/AGENTS.md"
CIRCUIT_STATE_FILE="${WORKSPACE}/skills/compact-guardian/circuit_state.json"
RECOVERY_LOG="${WORKSPACE}/.recovery/failures.json"
SESSION_DIR="${HOME}/.openclaw/agents/main/sessions"

MEMORY_LIMIT=15000  # 字符数限制
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_NC='\033[0m'  # No Color

# 处理参数：支持 --json, --html 或直接 json, html
OUTPUT_FORMAT="text"
if [ $# -gt 0 ]; then
    case "$1" in
        --json|json)
            OUTPUT_FORMAT="json"
            ;;
        --html|html)
            OUTPUT_FORMAT="html"
            ;;
        text|--text)
            OUTPUT_FORMAT="text"
            ;;
    esac
fi

# ─── 辅助函数 ─────────────────────────────────────────────────────────────

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >&2
}

error() {
    echo -e "${COLOR_RED}❌ ERROR${COLOR_NC}: $1" >&2
}

success() {
    echo -e "${COLOR_GREEN}✓ $1${COLOR_NC}"
}

warning() {
    echo -e "${COLOR_YELLOW}⚠️  $1${COLOR_NC}"
}

# 格式化百分比条形
progress_bar() {
    local percent=$1
    local width=10
    local filled=$((percent * width / 100))
    local empty=$((width - filled))

    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf " %3d%%\n" "$percent"
}

# 人类可读的时间差
time_ago() {
    local timestamp=$1
    local now=$(date +%s)
    local diff=$((now - timestamp))

    if [ $diff -lt 60 ]; then
        echo "${diff}s ago"
    elif [ $diff -lt 3600 ]; then
        echo "$((diff / 60))m ago"
    elif [ $diff -lt 86400 ]; then
        echo "$((diff / 3600))h ago"
    else
        echo "$((diff / 86400))d ago"
    fi
}

# ─── 检查指标 ─────────────────────────────────────────────────────────────

check_memory_capacity() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "0 0"
        return
    fi

    local size=$(wc -c < "$MEMORY_FILE")
    local percent=$((size * 100 / MEMORY_LIMIT))
    echo "$size $percent"
}

check_last_compaction() {
    local state_file="${WORKSPACE}/.memory_compaction_state.json"

    if [ ! -f "$state_file" ]; then
        echo "never 0"
        return
    fi

    # 从状态文件中提取最后运行时间（假设是 JSON 格式）
    if command -v jq &> /dev/null; then
        local last_run=$(jq -r '.last_run // empty' "$state_file" 2>/dev/null || echo "0")
        if [ -n "$last_run" ] && [ "$last_run" != "0" ]; then
            local ago=$(time_ago "$last_run")
            echo "success $ago"
        else
            echo "unknown 0"
        fi
    else
        echo "unknown 0"
    fi
}

check_guardian_status() {
    if [ ! -f "$CIRCUIT_STATE_FILE" ]; then
        echo "active 0"
        return
    fi

    if command -v jq &> /dev/null; then
        local status=$(jq -r '.circuit_status // "active"' "$CIRCUIT_STATE_FILE" 2>/dev/null || echo "active")
        local failures=$(jq -r '.current_failures // 0' "$CIRCUIT_STATE_FILE" 2>/dev/null || echo "0")
        echo "$status $failures"
    else
        echo "active 0"
    fi
}

count_rules_in_agents() {
    if [ ! -f "$AGENTS_FILE" ]; then
        echo "0 0 0"
        return
    fi

    local never=$(grep -c "^NEVER\|^- NEVER\|^  NEVER" "$AGENTS_FILE" 2>/dev/null || echo "0")
    local must=$(grep -c "^MUST\|^- MUST\|^  MUST" "$AGENTS_FILE" 2>/dev/null || echo "0")
    local always=$(grep -c "^ALWAYS\|^- ALWAYS\|^  ALWAYS" "$AGENTS_FILE" 2>/dev/null || echo "0")

    echo "$never $must $always"
}

count_recent_sessions() {
    if [ ! -d "$SESSION_DIR" ]; then
        echo "0"
        return
    fi

    # 查找最近 7 天的 session 文件
    local count=$(find "$SESSION_DIR" -type f -name "*.jsonl" -mtime -7 2>/dev/null | wc -l)
    echo "$count"
}

check_lancedb_size() {
    if [ ! -d "$LANCEDB_PATH" ]; then
        echo "0 0"
        return
    fi

    local size=$(du -sh "$LANCEDB_PATH" 2>/dev/null | awk '{print $1}')
    # 尝试查询记忆数（需要 sqlite3 或其他工具）
    local count="?"

    if command -v sqlite3 &> /dev/null 2>&1; then
        count=$(sqlite3 "$LANCEDB_PATH"/_manifest.sqlite "SELECT COUNT(*) FROM lance_datasets" 2>/dev/null || echo "?" )
    fi

    echo "$size $count"
}

count_recent_errors() {
    if [ ! -f "$RECOVERY_LOG" ]; then
        echo "0 0"
        return
    fi

    # 最近 24 小时的失败数
    local now=$(date +%s)
    local day_ago=$((now - 86400))

    if command -v jq &> /dev/null; then
        local count=$(jq "[.[] | select(.timestamp | fromdate > $day_ago)] | length" "$RECOVERY_LOG" 2>/dev/null || echo "0")
        # 最后一个错误
        local last=$(jq -r '.[-1].error // "none"' "$RECOVERY_LOG" 2>/dev/null || echo "unknown")
        echo "$count $last"
    else
        echo "0 unknown"
    fi
}

# ─── 输出格式 ─────────────────────────────────────────────────────────────

output_text() {
    local memory_info=$(check_memory_capacity)
    local memory_size=$(echo "$memory_info" | awk '{print $1}')
    local memory_percent=$(echo "$memory_info" | awk '{print $2}')

    local comp_info=$(check_last_compaction)
    local comp_status=$(echo "$comp_info" | awk '{print $1}')
    local comp_time=$(echo "$comp_info" | awk '{print $2}')

    local guard_info=$(check_guardian_status)
    local guard_status=$(echo "$guard_info" | awk '{print $1}')
    local guard_failures=$(echo "$guard_info" | awk '{print $2}')

    local rules_info=$(count_rules_in_agents)
    local never_rules=$(echo "$rules_info" | awk '{print $1}')
    local must_rules=$(echo "$rules_info" | awk '{print $2}')
    local always_rules=$(echo "$rules_info" | awk '{print $3}')

    local sessions=$(count_recent_sessions)
    local lancedb_info=$(check_lancedb_size)
    local lancedb_size=$(echo "$lancedb_info" | awk '{print $1}')

    local error_info=$(count_recent_errors)
    local error_count=$(echo "$error_info" | awk '{print $1}')
    local last_error=$(echo "$error_info" | awk '{print $2}')

    # 计算整体状态
    local status_icon="🟢"
    local status_color="$COLOR_GREEN"
    if [ "$memory_percent" -gt 80 ]; then
        status_icon="🟡"
        status_color="$COLOR_YELLOW"
    fi
    if [ "$memory_percent" -gt 100 ] || [ "$guard_status" = "open" ]; then
        status_icon="🔴"
        status_color="$COLOR_RED"
    fi

    echo ""
    echo -e "${status_color}${status_icon} OpenClaw System Health Check Report${COLOR_NC}"
    echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "┌─────────────────────────────────────────────────────────┐"

    # Memory Capacity
    echo -n "│ 💾 Memory Capacity      "
    if [ "$memory_percent" -gt 100 ]; then
        echo -ne "${COLOR_RED}"
    elif [ "$memory_percent" -gt 80 ]; then
        echo -ne "${COLOR_YELLOW}"
    else
        echo -ne "${COLOR_GREEN}"
    fi
    progress_bar "$memory_percent"
    echo -ne "${COLOR_NC}│ ($(numfmt --to=iec-i --suffix=B $memory_size 2>/dev/null || echo "${memory_size}B") / ${MEMORY_LIMIT})"
    echo ""

    # Last Compaction
    echo -n "│ ⏱️  Last Compaction     "
    if [ "$comp_status" = "success" ]; then
        echo -e "${COLOR_GREEN}✓${COLOR_NC} $comp_time"
    elif [ "$comp_status" = "never" ]; then
        echo -e "${COLOR_YELLOW}⚠️  Never run${COLOR_NC}"
    else
        echo -e "${COLOR_YELLOW}?${COLOR_NC} Unknown"
    fi

    # Guardian Status
    echo -n "│ 🛡️  Guardian Status     "
    if [ "$guard_status" = "active" ]; then
        echo -e "${COLOR_GREEN}🟢 Active${COLOR_NC} (failures: $guard_failures)"
    else
        echo -e "${COLOR_RED}🔴 Tripped${COLOR_NC} (failures: $guard_failures)"
    fi

    # Rules Count
    echo -n "│ 📋 Rules Count         "
    echo "NEVER: $never_rules | MUST: $must_rules | ALWAYS: $always_rules"

    # Recent Sessions
    echo "│ 📊 Recent Sessions      $sessions (7 days)"

    # LanceDB Size
    echo "│ 🗄️  LanceDB Size        $lancedb_size"

    # Errors
    echo -n "│ 🚨 Recent Errors       "
    if [ "$error_count" -eq 0 ]; then
        echo -e "${COLOR_GREEN}✓ 0 errors in 24h${COLOR_NC}"
    else
        echo -e "${COLOR_YELLOW}⚠️  $error_count errors (last: $last_error)${COLOR_NC}"
    fi

    echo "└─────────────────────────────────────────────────────────┘"
    echo ""
}

output_json() {
    local memory_info=$(check_memory_capacity)
    local comp_info=$(check_last_compaction)
    local guard_info=$(check_guardian_status)
    local rules_info=$(count_rules_in_agents)
    local sessions=$(count_recent_sessions)
    local lancedb_info=$(check_lancedb_size)
    local error_info=$(count_recent_errors)

    cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "memory": {
    "size_bytes": $(echo "$memory_info" | awk '{print $1}'),
    "usage_percent": $(echo "$memory_info" | awk '{print $2}'),
    "limit_bytes": $MEMORY_LIMIT
  },
  "compaction": {
    "status": "$(echo "$comp_info" | awk '{print $1}')",
    "last_run": "$(echo "$comp_info" | awk '{print $2}')"
  },
  "guardian": {
    "status": "$(echo "$guard_info" | awk '{print $1}')",
    "failures": $(echo "$guard_info" | awk '{print $2}')
  },
  "rules": {
    "never": $(echo "$rules_info" | awk '{print $1}'),
    "must": $(echo "$rules_info" | awk '{print $2}'),
    "always": $(echo "$rules_info" | awk '{print $3}')
  },
  "sessions": $sessions,
  "lancedb": {
    "size": "$(echo "$lancedb_info" | awk '{print $1}')"
  },
  "errors": {
    "count_24h": $(echo "$error_info" | awk '{print $1}'),
    "last_error": "$(echo "$error_info" | awk '{print $2}')"
  }
}
EOF
}

# ─── 主程序 ───────────────────────────────────────────────────────────────

main() {
    case "$OUTPUT_FORMAT" in
        json)
            output_json
            ;;
        html)
            # HTML 输出暂未实现，使用 text 替代
            output_text
            ;;
        *)
            output_text
            ;;
    esac
}

main
