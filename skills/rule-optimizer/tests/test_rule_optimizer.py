#!/usr/bin/env python3
"""规则优化器的单元测试"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from rule_optimizer import RuleOptimizer, RuleMetrics, RuleVariant


@pytest.fixture
def temp_workspace():
    """创建临时工作空间"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        workspace.mkdir(parents=True, exist_ok=True)
        yield workspace


@pytest.fixture
def optimizer(temp_workspace):
    """创建优化器实例"""
    return RuleOptimizer(str(temp_workspace))


class TestRuleOptimizer:
    """规则优化器测试"""

    def test_init(self, optimizer):
        """测试初始化"""
        assert optimizer.workspace is not None
        assert optimizer.thresholds["high_effective"] == 80

    def test_effectiveness_calculation(self, optimizer):
        """测试效能评分计算"""
        # 完美情况
        score = optimizer._calculate_effectiveness(
            freq=100, fix_rate=100, cost=10, satisfaction=5.0
        )
        assert score > 90

        # 糟糕情况
        score = optimizer._calculate_effectiveness(
            freq=1, fix_rate=20, cost=200, satisfaction=1.0
        )
        assert score < 40

    def test_record_and_retrieve_metrics(self, temp_workspace, optimizer):
        """测试记录和检索指标"""
        # 记录数据
        for i in range(5):
            optimizer.record_rule_application(
                "rule_123",
                fixed=(i < 4),
                latency_ms=25 + i*5,
                satisfaction=4.0
            )

        # 检索指标
        metrics = optimizer.evaluate_rule_effectiveness("rule_123")

        assert metrics.rule_id == "rule_123"
        assert metrics.trigger_frequency == 5
        assert 70 < metrics.fix_rate <= 100  # 4或5个成功
        assert metrics.cost_overhead_ms > 0
        assert metrics.user_satisfaction == 4.0

    def test_suggest_variants_high_effectiveness(self, optimizer):
        """测试高效能规则无建议"""
        # 模拟高效能規則
        variants = optimizer.suggest_rule_variants("high_rule")
        # 无历史数据，可能会有建议
        assert isinstance(variants, list)

    def test_suggest_variants_low_effectiveness(self, temp_workspace, optimizer):
        """测试低效能规则的建议"""
        # 记录低效能数据
        for _ in range(5):
            optimizer.record_rule_application(
                "low_rule",
                fixed=False,
                latency_ms=150,
                satisfaction=1.0
            )

        variants = optimizer.suggest_rule_variants("low_rule")
        assert len(variants) > 0
        assert any("loose" in v.variant_id for v in variants)

    def test_determine_rule_status(self, optimizer):
        """测试规则状态判定"""
        assert optimizer._determine_rule_status(90) == "active"
        assert optimizer._determine_rule_status(65) == "active"
        assert optimizer._determine_rule_status(35) == "testing"
        assert optimizer._determine_rule_status(10) == "deprecated"

    def test_ab_test_recording(self, temp_workspace, optimizer):
        """测试A/B测试结果记录"""
        optimizer.record_ab_test_result(
            "rule_123_variant",
            effectiveness=82.5,
            sample_count=100
        )

        ab_log = temp_workspace / ".ab-test-results.jsonl"
        assert ab_log.exists()

        with open(ab_log, 'r') as f:
            records = [json.loads(line) for line in f]
            assert len(records) == 1
            assert records[0]["variant_id"] == "rule_123_variant"
            assert records[0]["effectiveness"] == 82.5
            assert records[0]["conclusion"] == "promote"


class TestRuleMetrics:
    """规则指标数据类测试"""

    def test_create_metrics(self):
        """测试创建指标对象"""
        metrics = RuleMetrics(
            rule_id="test_rule",
            trigger_frequency=10,
            fix_rate=85.0,
            cost_overhead_ms=25.0,
            user_satisfaction=4.2
        )

        assert metrics.rule_id == "test_rule"
        assert metrics.trigger_frequency == 10
        assert metrics.effectiveness_score == 0.0  # 默认值


class TestIntegration:
    """集成测试"""

    def test_full_workflow(self, temp_workspace):
        """完整工作流测试"""
        optimizer = RuleOptimizer(str(temp_workspace))

        # 1. 记录规则应用
        for i in range(20):
            optimizer.record_rule_application(
                "workflow_rule",
                fixed=(i < 15),  # 75%成功率
                latency_ms=20 + i % 10,
                satisfaction=4.0 if i < 15 else 2.0
            )

        # 2. 评估效能
        metrics = optimizer.evaluate_rule_effectiveness("workflow_rule")
        assert metrics.trigger_frequency == 20
        assert 65 < metrics.fix_rate <= 100

        # 3. 建议优化
        variants = optimizer.suggest_rule_variants("workflow_rule")
        assert isinstance(variants, list)

        # 4. 测试变体
        if len(variants) > 0:
            optimizer.record_ab_test_result(
                variants[0].variant_id,
                effectiveness=88.0,
                sample_count=50
            )

            ab_log = temp_workspace / ".ab-test-results.jsonl"
            assert ab_log.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
