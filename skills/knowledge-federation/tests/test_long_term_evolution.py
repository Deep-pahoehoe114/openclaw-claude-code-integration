#!/usr/bin/env python3
"""
test_long_term_evolution.py - 长期演化系统测试
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

from skills.knowledge_federation.scripts.long_term_evolution import (
    AIRuleOptimizer, CrossProjectKnowledgeTransfer, IntelligentConflictResolver,
    ObservabilityDashboard, RuleMetrics, ProjectContext, KnowledgeTransfer,
    OptimizationSuggestion, SystemMetrics,
)


class TestAIRuleOptimizer:
    """AI驱动规则优化测试"""

    def test_fallback_suggestions(self, tmp_path):
        """测试回退建议生成"""
        optimizer = AIRuleOptimizer(workspace_dir=str(tmp_path))

        metrics = RuleMetrics(
            rule_id="test_rule",
            version_id="v1",
            effectiveness_score=55.0,
            success_count=10,
            failure_count=5,
            avg_latency_ms=150.0,
            user_satisfaction=3.5,
            last_updated=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        )

        suggestions = optimizer._fallback_suggestions("test_rule", metrics)

        assert len(suggestions) > 0
        assert any(s.suggested_change.get("action") == "loosen_condition" for s in suggestions)

    def test_build_context_text(self, tmp_path):
        """测试上下文文本构建"""
        optimizer = AIRuleOptimizer(workspace_dir=str(tmp_path))

        metrics = RuleMetrics(
            rule_id="test_rule",
            version_id="v1",
            effectiveness_score=75.0,
            success_count=20,
            failure_count=2,
            avg_latency_ms=50.0,
            user_satisfaction=4.0,
            last_updated=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        )

        context = optimizer._build_context_text("test_rule", metrics)

        assert "test_rule" in context
        assert "75.0" in context

    def test_apply_suggestion(self, tmp_path):
        """测试应用建议"""
        optimizer = AIRuleOptimizer(workspace_dir=str(tmp_path))

        suggestion = OptimizationSuggestion(
            suggestion_id="test_opt_1",
            rule_id="test_rule",
            current_state={"effectiveness": 70.0},
            suggested_change={"action": "test"},
            rationale="test",
            expected_improvement=0.1,
            confidence=0.8,
        )

        result = optimizer.apply_suggestion(suggestion)

        assert result is True
        assert optimizer.metrics_dir.exists()


class TestCrossProjectKnowledgeTransfer:
    """跨项目知识转移测试"""

    def test_register_project(self, tmp_path):
        """测试项目注册"""
        transfer = CrossProjectKnowledgeTransfer(workspace_dir=str(tmp_path))

        transfer.register_project("proj_a", "python", {"python", "backend"})
        transfer.register_project("proj_b", "python", {"python", "api"})

        assert "proj_a" in transfer.project_profiles
        assert "proj_b" in transfer.project_profiles
        assert transfer.project_profiles["proj_a"].project_type == "python"

    def test_analyze_similarity(self, tmp_path):
        """测试相似度分析"""
        transfer = CrossProjectKnowledgeTransfer(workspace_dir=str(tmp_path))

        transfer.register_project("proj_a", "python", {"python", "backend"})
        transfer.register_project("proj_b", "python", {"python", "api"})
        transfer.register_project("proj_c", "rust", {"rust", "systems"})

        # 相同类型
        ab_sim = transfer.analyze_project_similarity("proj_a", "proj_b")
        assert ab_sim > 0.5

        # 不同类型
        ac_sim = transfer.analyze_project_similarity("proj_a", "proj_c")
        assert ac_sim < ab_sim

    def test_find_similar_projects(self, tmp_path):
        """测试查找相似项目"""
        transfer = CrossProjectKnowledgeTransfer(workspace_dir=str(tmp_path))

        transfer.register_project("proj_a", "python", {"python", "backend", "api"})
        transfer.register_project("proj_b", "python", {"python", "backend"})
        transfer.register_project("proj_c", "javascript", {"javascript", "frontend"})
        transfer.register_project("proj_d", "rust", {"rust", "systems"})

        similar = transfer.find_similar_projects("proj_a", min_similarity=0.3)

        assert len(similar) >= 2
        # proj_b 应该最相似
        assert similar[0][0] == "proj_b"

    def test_transfer_history(self, tmp_path):
        """测试转移历史"""
        transfer = CrossProjectKnowledgeTransfer(workspace_dir=str(tmp_path))

        history = transfer.get_transfer_history()
        assert len(history) == 0


class TestIntelligentConflictResolver:
    """智能冲突解决测试"""

    def test_analyze_conflict(self):
        """测试冲突分析"""
        resolver = IntelligentConflictResolver()

        local_rule = {
            "rule_id": "local_rule",
            "effectiveness_score": 70.0,
            "content": {"timeout": 10, "retry": 3},
        }

        community_rule = {
            "rule_id": "local_rule",
            "effectiveness_score": 85.0,
            "content": {"timeout": 5, "retry": 5, "cache": True},
        }

        analysis = resolver.analyze_conflict(local_rule, community_rule)

        assert "recommendation" in analysis
        assert "strategies" in analysis
        assert analysis["score_gap"] == 15.0

    def test_generate_recommendation(self):
        """测试推荐生成"""
        resolver = IntelligentConflictResolver()

        # 分差大，本地赢
        rec = resolver._generate_recommendation(85, 60, 25, 0.5)
        assert rec == "LOCAL_PRIORITY"

        # 分差大，社群赢
        rec = resolver._generate_recommendation(55, 85, 30, 0.5)
        assert rec == "COMMUNITY_PRIORITY"

        # 分差小，内容相似
        rec = resolver._generate_recommendation(75, 78, 3, 0.85)
        assert rec == "MERGE"

    def test_suggest_strategies(self):
        """测试策略建议"""
        resolver = IntelligentConflictResolver()

        strategies = resolver._suggest_strategies(75, 85, 0.6)

        assert len(strategies) >= 2
        assert any(s["strategy"] == "LOCAL_PRIORITY" for s in strategies)
        assert any(s["strategy"] == "COMMUNITY_PRIORITY" for s in strategies)


class TestObservabilityDashboard:
    """可观测性仪表板测试"""

    def test_health_color(self, tmp_path):
        """测试健康分颜色"""
        dashboard = ObservabilityDashboard(workspace_dir=str(tmp_path))

        assert dashboard._health_color(90) == "#4CAF50"  # 绿色
        assert dashboard._health_color(70) == "#FFC107"  # 黄色
        assert dashboard._health_color(50) == "#F44336"  # 红色

    def test_compute_local_metrics(self, tmp_path):
        """测试本地指标计算"""
        dashboard = ObservabilityDashboard(workspace_dir=str(tmp_path))

        metrics = dashboard._compute_local_metrics()

        assert isinstance(metrics, SystemMetrics)
        assert metrics.total_rules >= 0
        assert metrics.health_score >= 0

    def test_generate_dashboard_html(self, tmp_path):
        """测试HTML生成"""
        dashboard = ObservabilityDashboard(workspace_dir=str(tmp_path))

        html = dashboard.generate_dashboard_html()

        assert "<!DOCTYPE html>" in html
        assert "OpenClaw" in html
        assert "系统健康分" in html

    def test_save_dashboard(self, tmp_path):
        """测试仪表板保存"""
        dashboard = ObservabilityDashboard(workspace_dir=str(tmp_path))

        output_path = tmp_path / "test_dashboard.html"
        result = dashboard.save_dashboard(str(output_path))

        assert Path(result).exists()
        assert "test_dashboard.html" in result

    def test_cache_validity(self, tmp_path):
        """测试缓存有效性"""
        dashboard = ObservabilityDashboard(workspace_dir=str(tmp_path))

        # 空缓存应无效
        assert dashboard._is_cache_valid() is False


class TestRuleMetrics:
    """规则指标测试"""

    def test_create_metrics(self):
        """测试创建指标"""
        metrics = RuleMetrics(
            rule_id="test",
            version_id="v1",
            effectiveness_score=85.0,
            success_count=20,
            failure_count=2,
            avg_latency_ms=45.0,
            user_satisfaction=4.5,
            last_updated=datetime.now().isoformat(),
        )

        assert metrics.rule_id == "test"
        assert metrics.effectiveness_score == 85.0


class TestKnowledgeTransfer:
    """知识转移测试"""

    def test_create_transfer(self):
        """测试创建转移记录"""
        transfer = KnowledgeTransfer(
            transfer_id="t1",
            source_project="proj_a",
            target_project="proj_b",
            transferred_rules=["rule1", "rule2"],
            similarity_score=0.75,
            effectiveness_gain=5.0,
            timestamp=datetime.now().isoformat(),
        )

        assert transfer.transferred_rules == ["rule1", "rule2"]
        assert transfer.similarity_score == 0.75


if __name__ == "__main__":
    pytest.main([__file__, "-v"])