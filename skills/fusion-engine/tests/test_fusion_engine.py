#!/usr/bin/env python3
"""
多源融合引擎的单元测试
"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from fusion_engine import MultiSourceFusionEngine, FusionScore


@pytest.fixture
def temp_workspace():
    """创建临时工作空间"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)

        # 创建必要的目录
        (workspace / "memory" / "lancedb-pro").mkdir(parents=True)

        yield workspace


@pytest.fixture
def engine(temp_workspace):
    """创建融合引擎实例"""
    return MultiSourceFusionEngine(str(temp_workspace))


class TestMultiSourceFusionEngine:
    """多源融合引擎测试"""

    def test_init(self, engine):
        """测试初始化"""
        assert engine.workspace is not None
        assert engine.weights["memory"] == 0.30
        assert engine.thresholds["auto_allow"] == 75

    def test_fuse_decision_context_basic(self, engine):
        """测试基础融合决策"""
        score = engine.fuse_decision_context("bash", {"command": "ls"})

        assert isinstance(score, FusionScore)
        assert 0 <= score.memory_relevance <= 100
        assert 0 <= score.cmd_success_rate <= 100
        assert 0 <= score.user_preference <= 100
        assert 0 <= score.system_health <= 100
        assert 0 <= score.final_score <= 100
        assert score.decision in ["auto_allow", "request_confirm", "block"]

    def test_memory_relevance_no_history(self, engine):
        """测试无历史记忆时的相关性"""
        score = engine._evaluate_memory_relevance("bash", {"command": "ls"})
        assert 30 < score < 60  # 应该返回中等分数

    def test_cmd_success_rate_no_history(self, engine):
        """测试无执行历史时的成功率"""
        score = engine._evaluate_cmd_success_rate("bash", {"command": "ls"})
        assert score == 60  # 应该返回保守分数

    def test_user_preference_no_history(self, engine):
        """测试无用户交互历史时的偏好"""
        score = engine._evaluate_user_preference("write", {"file": "test.txt"})
        assert score == 50  # 应该返回中间分数

    def test_cmd_success_rate_with_history(self, temp_workspace, engine):
        """测试有执行历史时的成功率计算"""
        # 创建命令执行日志
        cmd_log = temp_workspace / ".command-execution.jsonl"
        with open(cmd_log, 'w') as f:
            for i in range(10):
                record = {
                    "tool": "bash",
                    "status": "success" if i < 8 else "failure",
                    "timestamp": datetime.now().isoformat()
                }
                f.write(json.dumps(record) + '\n')

        score = engine._evaluate_cmd_success_rate("bash", {"command": "ls"})
        assert 75 < score <= 85  # 8/10 = 80%

    def test_user_preference_with_history(self, temp_workspace, engine):
        """测试有用户交互历史时的偏好"""
        # 创建用户交互日志
        user_log = temp_workspace / ".user-interactions.jsonl"
        with open(user_log, 'w') as f:
            for i in range(10):
                record = {
                    "tool": "write",
                    "action": "approved" if i < 7 else "rejected",
                    "satisfaction": 5 if i < 7 else 1,
                    "timestamp": datetime.now().isoformat()
                }
                f.write(json.dumps(record) + '\n')

        score = engine._evaluate_user_preference("write", {"file": "test.txt"})
        # 70%接受率 + 平均满意度应该给出较高分数
        assert score > 60

    def test_weighted_fusion_calculation(self, engine):
        """测试加权融合计算"""
        # 都是满分
        result = engine._weighted_fusion(100, 100, 100, 100)
        assert result == 100

        # 都是0分
        result = engine._weighted_fusion(0, 0, 0, 0)
        assert result == 0

        # 混合分数
        result = engine._weighted_fusion(80, 80, 80, 60)
        # 80*0.3 + 80*0.3 + 80*0.25 + 60*0.15 = 24 + 24 + 20 + 9 = 77
        assert 76 < result < 78

    def test_make_decision_auto_allow(self, engine):
        """测试自动允许决策"""
        decision = engine._make_decision(80)
        assert decision == "auto_allow"

    def test_make_decision_request_confirm(self, engine):
        """测试请求确认决策"""
        decision = engine._make_decision(60)
        assert decision == "request_confirm"

    def test_make_decision_block(self, engine):
        """测试阻止决策"""
        decision = engine._make_decision(30)
        assert decision == "block"

    def test_system_health_evaluation(self, engine):
        """测试系统健康评估"""
        score = engine._evaluate_system_health()
        # 系统健康分数应该是合理的
        assert 10 <= score <= 100
        # 在正常系统上应该有不错的分数
        assert score > 20

    def test_save_decision(self, temp_workspace, engine):
        """测试保存融合决策"""
        score = FusionScore(
            memory_relevance=80.0,
            cmd_success_rate=85.0,
            user_preference=75.0,
            system_health=70.0,
            final_score=77.5,
            decision="request_confirm",
            reasoning={}
        )

        engine.save_decision("bash", score, "test_session")

        fusion_log = temp_workspace / ".fusion-decisions.jsonl"
        assert fusion_log.exists()

        with open(fusion_log, 'r') as f:
            content = f.read()
            assert "bash" in content
            assert "77.5" in content


class TestFusionScoreDataclass:
    """FusionScore数据类测试"""

    def test_create_fusion_score(self):
        """测试创建融合评分"""
        score = FusionScore(
            memory_relevance=75.5,
            cmd_success_rate=80.0,
            user_preference=70.5,
            system_health=65.0,
            final_score=73.5,
            decision="request_confirm",
            reasoning={"test": "reason"}
        )

        assert score.memory_relevance == 75.5
        assert score.final_score == 73.5
        assert score.decision == "request_confirm"

    def test_fusion_score_to_dict(self):
        """测试转换为字典"""
        from dataclasses import asdict

        score = FusionScore(
            memory_relevance=75.0,
            cmd_success_rate=80.0,
            user_preference=70.0,
            system_health=65.0,
            final_score=73.0,
            decision="request_confirm",
            reasoning={}
        )

        d = asdict(score)
        assert isinstance(d, dict)
        assert d["final_score"] == 73.0


class TestIntegration:
    """集成测试"""

    def test_end_to_end_scoring(self, temp_workspace):
        """端到端测试：从创建引擎到生成决策"""
        # 准备数据
        engine = MultiSourceFusionEngine(str(temp_workspace))

        # 添加命令执行历史
        cmd_log = temp_workspace / ".command-execution.jsonl"
        with open(cmd_log, 'w') as f:
            f.write(json.dumps({"tool": "bash", "status": "success"}) + '\n')
            f.write(json.dumps({"tool": "bash", "status": "success"}) + '\n')

        # 添加用户交互历史
        user_log = temp_workspace / ".user-interactions.jsonl"
        with open(user_log, 'w') as f:
            f.write(json.dumps({
                "tool": "bash",
                "action": "approved",
                "satisfaction": 5
            }) + '\n')

        # 执行融合
        score = engine.fuse_decision_context("bash", {"command": "ls"}, "session_1")

        # 验证结果
        assert score.cmd_success_rate > 50  # 有历史记录
        assert score.user_preference > 50   # 有积极的用户反馈
        assert score.final_score > 0
        assert score.decision in ["auto_allow", "request_confirm", "block"]

    def test_different_tools_different_scores(self, temp_workspace):
        """测试不同工具的不同评分"""
        engine = MultiSourceFusionEngine(str(temp_workspace))

        # bash: 较高风险
        score1 = engine.fuse_decision_context("bash", {"command": "rm -rf /"})
        # read: 较低风险
        score2 = engine.fuse_decision_context("read", {"file": "test.txt"})

        # 两者都应该有有效的分数，但可能存在差异
        assert 0 <= score1.final_score <= 100
        assert 0 <= score2.final_score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
