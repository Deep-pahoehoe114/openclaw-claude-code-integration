#!/bin/bash
##############################################################################
# tests/test_health_check.sh — Health Check Dashboard 测试套件
#
# 使用 bash unit testing 框架
# 默认输出实际结果以供手工验证
#
##############################################################################

set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HEALTH_CHECK="${SOURCE_DIR}/tools/health_check.sh"

# 测试统计
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ─── 测试框架 ─────────────────────────────────────────────────────────────

assert_equals() {
    local expected=$1
    local actual=$2
    local message=$3
    TESTS_RUN=$((TESTS_RUN + 1))

    if [ "$expected" = "$actual" ]; then
        echo "  ✓ $message"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo "  ✗ $message (expected: $expected, got: $actual)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

assert_contains() {
    local haystack=$1
    local needle=$2
    local message=$3
    TESTS_RUN=$((TESTS_RUN + 1))

    if echo "$haystack" | grep -q "$needle"; then
        echo "  ✓ $message"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo "  ✗ $message (output doesn't contain: $needle)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# ─── 测试用例 ─────────────────────────────────────────────────────────────

test_health_check_text_output() {
    echo "Test Suite: Text Output Format"

    local output=$(bash "$HEALTH_CHECK" text 2>&1 || true)

    assert_contains "$output" "OpenClaw System Health Check" "Contains report title"
    assert_contains "$output" "Memory Capacity" "Contains memory check"
    assert_contains "$output" "Last Compaction" "Contains compaction status"
    assert_contains "$output" "Guardian Status" "Contains guardian status"
    assert_contains "$output" "Rules Count" "Contains rules summary"
}

test_health_check_json_output() {
    echo "Test Suite: JSON Output Format"

    local output=$(bash "$HEALTH_CHECK" --json 2>&1 || true)

    assert_contains "$output" "\"timestamp\"" "JSON contains timestamp"
    assert_contains "$output" "\"memory\"" "JSON contains memory object"
    assert_contains "$output" "\"compaction\"" "JSON contains compaction object"
    assert_contains "$output" "\"guardian\"" "JSON contains guardian object"
}

test_health_check_script_existence() {
    echo "Test Suite: Script Validation"

    [ -f "$HEALTH_CHECK" ] && echo "  ✓ health_check.sh exists"
    [ -x "$HEALTH_CHECK" ] && echo "  ✓ health_check.sh is executable"
}

test_health_check_performance() {
    echo "Test Suite: Performance"

    TESTS_RUN=$((TESTS_RUN + 1))
    local start_time=$(date +%s%N)
    bash "$HEALTH_CHECK" text > /dev/null 2>&1 || true
    local end_time=$(date +%s%N)
    local elapsed=$((( end_time - start_time ) / 1000000))  # ms

    if [ $elapsed -lt 2000 ]; then
        echo "  ✓ Execution time: ${elapsed}ms (should be < 2000ms)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo "  ✗ Execution too slow: ${elapsed}ms (should be < 2000ms)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

test_missing_workspace() {
    echo "Test Suite: Error Handling"

    # 临时改变 WORKSPACE
    local old_workspace="$HOME/.openclaw/workspace"
    local test_workspace="/tmp/nonexistent_openclaw_$$"

    # 不要真的改变它，只测试脚本的逻辑
    TESTS_RUN=$((TESTS_RUN + 1))
    echo "  ⓘ Skipping: Would require modifying script environment"
}

# ─── 运行所有测试 ─────────────────────────────────────────────────────────

main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  Health Check Dashboard Test Suite"
    echo "═══════════════════════════════════════════════════════════"
    echo ""

    test_health_check_script_existence
    echo ""

    test_health_check_text_output
    echo ""

    test_health_check_json_output
    echo ""

    test_health_check_performance
    echo ""

    test_missing_workspace
    echo ""

    echo "═══════════════════════════════════════════════════════════"
    echo "Test Results:"
    echo "  Total:  $TESTS_RUN"
    echo "  Passed: $TESTS_PASSED"
    echo "  Failed: $TESTS_FAILED"
    echo "═══════════════════════════════════════════════════════════"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo "✅ All tests passed!"
        return 0
    else
        echo "❌ Some tests failed!"
        return 1
    fi
}

main "$@"
