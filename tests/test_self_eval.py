"""
test_self_eval.py — Tests for self_eval.py (reflection detection & LanceDB write)

Covers:
- reflection detection from session messages
- LanceDB write (mocked)
- build_reflection_text output format
- silent exit on normal sessions
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).parent.parent / "skills" / "self-eval" / "scripts"),
)
from self_eval import (
    detect_corrections,
    detect_tool_failures,
    detect_bdx_failures,
    detect_pause_rules,
    build_reflection_text,
    store_reflection,
)


class TestDetectCorrections:
    def test_detects_chinese_correction(self, sample_messages_with_correction):
        findings = detect_corrections(sample_messages_with_correction)
        assert len(findings) >= 1
        assert any(f["type"] == "user_correction" for f in findings)

    def test_no_false_positives_on_normal_text(self, sample_messages):
        findings = detect_corrections(sample_messages)
        assert len(findings) == 0

    def test_no_false_positive_on_market_wrong(self):
        """'市场不对' should be excluded as context-specific, not AI correction."""
        messages = [
            {"role": "user", "content": "市场不对，数据需要更新"}
        ]
        findings = detect_corrections(messages)
        assert len(findings) == 0

    def test_english_no_correction(self):
        messages = [{"role": "user", "content": "the result is incorrect"}]
        findings = detect_corrections(messages)
        assert len(findings) == 0

    def test_empty_messages(self):
        findings = detect_corrections([])
        assert findings == []


class TestDetectToolFailures:
    def test_detects_retry_failure(self, sample_messages_with_tool_failure):
        findings = detect_tool_failures(sample_messages_with_tool_failure)
        assert len(findings) >= 1
        assert any(f["type"] == "tool_failure" for f in findings)

    def test_empty_messages(self):
        findings = detect_tool_failures([])
        assert findings == []


class TestDetectPauseRules:
    def test_detects_pause_pattern(self, sample_messages_with_pause):
        findings = detect_pause_rules(sample_messages_with_pause)
        assert len(findings) >= 1
        assert any(f["type"] == "pause_confirm" for f in findings)

    def test_empty_messages(self):
        findings = detect_pause_rules([])
        assert findings == []


class TestBuildReflectionText:
    def test_user_correction_text(self):
        finding = {
            "type": "user_correction",
            "pattern": r"不对",
            "excerpt": "不对，我想要的是上海",
        }
        text = build_reflection_text(finding)
        assert len(text) > 0
        assert "用户纠正" in text or "纠正" in text

    def test_tool_failure_text(self):
        finding = {
            "type": "tool_failure",
            "pattern": r"重试.*仍失败",
            "excerpt": "工具重试3次仍失败",
        }
        text = build_reflection_text(finding)
        assert len(text) > 0
        assert "工具" in text or "失败" in text

    def test_bdx_failure_text(self):
        finding = {
            "type": "bdx_failure",
            "pattern": r"BDX.*失败",
            "excerpt": "BDX回测失败",
        }
        text = build_reflection_text(finding)
        assert len(text) > 0

    def test_pause_confirm_text(self):
        finding = {
            "type": "pause_confirm",
            "pattern": r"需要我确认",
            "excerpt": "需要我确认后再执行",
        }
        text = build_reflection_text(finding)
        assert len(text) > 0
        assert "确认" in text

    def test_unknown_type_empty(self):
        finding = {"type": "unknown_type"}
        text = build_reflection_text(finding)
        assert text == ""


class TestStoreReflection:
    def test_store_reflection_calls_lancedb(self, mock_lancedb, mock_minimax_api):
        ok = store_reflection(
            category="reflection",
            content="测试：用户纠正场景下的反思",
            importance=0.9,
        )
        assert ok is True
        # verify data was added
        table = mock_lancedb.open_table("memories")
        assert len(table._rows) == 1
        assert table._rows[0]["category"] == "reflection"

    def test_store_reflection_importance(self, mock_lancedb, mock_minimax_api):
        store_reflection(
            category="reflection",
            content="工具失败反思",
            importance=0.95,
        )
        table = mock_lancedb.open_table("memories")
        assert table._rows[0]["importance"] == 0.95
