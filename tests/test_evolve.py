"""
test_evolve.py — Tests for evolve.py (rule extraction from reflection memories)

Covers:
- classify_reflection() categorization
- generate_rules() NEVER/MUST format output
- empty memory handling
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).parent.parent / "skills" / "evolve" / "scripts"),
)
from evolve import (
    classify_reflection,
    extract_rule_candidates,
    generate_rules,
)


class TestClassifyReflection:
    def test_user_correction(self):
        text = "用户纠正：不对，我想要的是上海"
        result = classify_reflection(text)
        assert result == "用户纠正"

    def test_tool_failure(self):
        text = "工具调用失败，重试3次仍失败"
        result = classify_reflection(text)
        assert result == "工具失败"

    def test_pause_confirm(self):
        text = "需要我确认后再执行，涉及生产参数"
        result = classify_reflection(text)
        assert result == "上报触发"

    def test_other_falls_through(self):
        text = "这是一个普通的对话记录，没有触发任何规则"
        result = classify_reflection(text)
        assert result == "其他"


class TestExtractRuleCandidates:
    def test_group_by_category(self):
        memories = [
            {"text": "不对，我想要的是上海", "metadata": "{}"},
            {"text": "工具调用失败重试3次仍失败", "metadata": "{}"},
            {"text": "需要我确认后再执行", "metadata": "{}"},
        ]
        grouped = extract_rule_candidates(memories)
        assert len(grouped["用户纠正"]) == 1
        assert len(grouped["工具失败"]) == 1
        assert len(grouped["上报触发"]) == 1

    def test_empty_list(self):
        grouped = extract_rule_candidates([])
        assert grouped["用户纠正"] == []
        assert grouped["工具失败"] == []
        assert grouped["上报触发"] == []


class TestGenerateRules:
    def test_never_rule_for_tool_failure(self):
        grouped = {
            "用户纠正": [],
            "工具失败": [("工具失败文本1", "{}")],
            "上报触发": [],
            "其他": [],
        }
        rules = generate_rules(grouped)
        assert len(rules) >= 1
        keywords = [r[0] for r in rules]
        assert "NEVER" in keywords or "MUST" in keywords

    def test_must_rule_for_user_correction(self):
        grouped = {
            "用户纠正": [("纠正文本1", "{}"), ("纠正文本2", "{}")],
            "工具失败": [],
            "上报触发": [],
            "其他": [],
        }
        rules = generate_rules(grouped)
        assert len(rules) >= 1
        rule_texts = [r[1] for r in rules]
        assert any("纠正" in t for t in rule_texts)

    def test_must_rule_for_escalation(self):
        grouped = {
            "用户纠正": [],
            "工具失败": [],
            "上报触发": [("确认文本1", "{}")],
            "其他": [],
        }
        rules = generate_rules(grouped)
        assert len(rules) >= 1

    def test_empty_grouping_produces_no_rules(self):
        grouped = {
            "用户纠正": [],
            "工具失败": [],
            "上报触发": [],
            "其他": [],
        }
        rules = generate_rules(grouped)
        assert rules == []

    def test_rule_format_contains_trigger_count(self):
        grouped = {
            "用户纠正": [("纠正1", "{}")],
            "工具失败": [],
            "上报触发": [],
            "其他": [],
        }
        rules = generate_rules(grouped)
        assert len(rules) == 1
        keyword, rule_text = rules[0]
        assert keyword in ("MUST", "NEVER")
        assert "触发次数" in rule_text
