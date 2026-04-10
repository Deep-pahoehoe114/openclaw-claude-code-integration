#!/usr/bin/env python3
"""知识共享框架的单元测试"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from knowledge_federation import (
    KnowledgeFederation, LocalRuleRegistry, ConflictResolver,
    CommunityLeaderboard, RuleVersion, RuleConflict, CommunityRule,
    RuleSource, ConflictResolution
)


@pytest.fixture
def temp_workspace():
    """创建临时工作空间"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        workspace.mkdir(parents=True, exist_ok=True)
        yield workspace


@pytest.fixture
def local_registry(temp_workspace):
    """创建本地规则库实例"""
    return LocalRuleRegistry(str(temp_workspace))


@pytest.fixture
def fed(temp_workspace):
    """创建知识联邦实例"""
    return KnowledgeFederation(str(temp_workspace))


class TestRuleVersion:
    """RuleVersion数据类测试"""

    def test_create_rule_version(self):
        """测试创建规则版本"""
        version = RuleVersion(
            version_id="v1",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_1",
            timestamp=datetime.now().isoformat(),
            content={"condition": "x > 5"},
            effectiveness_score=85.0,
            status="published",
            tags=["critical", "security"],
            description="Initial version",
            breaking_changes=[]
        )

        assert version.version_id == "v1"
        assert version.rule_id == "rule_123"
        assert version.effectiveness_score == 85.0
        assert version.status == "published"
        assert "critical" in version.tags


class TestCommunityRule:
    """CommunityRule数据类测试"""

    def test_create_community_rule(self):
        """测试创建社群规则"""
        rule = CommunityRule(
            rule_id="rule_abc",
            versions=[],
            effectiveness_history=[],
            adoption_count=5,
            project_tags={"finance", "security"}
        )

        assert rule.rule_id == "rule_abc"
        assert rule.adoption_count == 5
        assert "finance" in rule.project_tags


class TestLocalRuleRegistry:
    """本地规则库测试"""

    def test_init(self, local_registry):
        """测试初始化"""
        assert local_registry.workspace is not None
        assert local_registry.rules_dir.exists()

    def test_register_rule(self, local_registry):
        """测试注册规则"""
        version = local_registry.register_rule(
            rule_id="rule_test",
            content={"action": "deny"},
            effectiveness=90.0,
            description="Test rule"
        )

        assert version.rule_id == "rule_test"
        assert version.effectiveness_score == 90.0
        assert version.status == "draft"
        assert version.author_agent == "local"

    def test_persist_and_retrieve(self, local_registry):
        """测试规则持久化和检索"""
        # 注册规则
        version = local_registry.register_rule(
            "persist_test",
            {"config": "value"},
            75.0
        )

        # 检索规则
        retrieved = local_registry.get_rule("persist_test")
        assert retrieved is not None
        assert retrieved.rule_id == "persist_test"
        assert retrieved.effectiveness_score == 75.0

    def test_list_rules(self, local_registry):
        """测试列出所有规则"""
        local_registry.register_rule("rule_1", {}, 80.0)
        local_registry.register_rule("rule_2", {}, 70.0)
        local_registry.register_rule("rule_3", {}, 60.0)

        rules = local_registry.list_rules()
        assert len(rules) == 3
        assert all(r.rule_id in ["rule_1", "rule_2", "rule_3"] for r in rules)

    def test_rule_file_persistence(self, local_registry, temp_workspace):
        """测试规则文件持久化"""
        version = local_registry.register_rule(
            "persist_file_test",
            {"data": "test"},
            85.0
        )

        # 验证文件存在
        rule_file = temp_workspace / ".local-rules" / f"persist_file_test_{version.version_id}.json"
        assert rule_file.exists()

        # 读取文件内容
        with open(rule_file, 'r') as f:
            content = json.load(f)
            assert content["rule_id"] == "persist_file_test"
            assert content["effectiveness_score"] == 85.0


class TestConflictResolver:
    """规则冲突解决器测试"""

    def test_detect_conflicts_same_content(self):
        """测试检测相同内容的规则-无冲突"""
        local_rule = RuleVersion(
            version_id="v1",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_1",
            timestamp=datetime.now().isoformat(),
            content={"action": "allow"},
            effectiveness_score=80.0,
            status="published"
        )

        community_rule = RuleVersion(
            version_id="v2",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_2",
            timestamp=datetime.now().isoformat(),
            content={"action": "allow"},
            effectiveness_score=85.0,
            status="published"
        )

        assert not ConflictResolver.detect_conflicts(local_rule, community_rule)

    def test_detect_conflicts_different_content(self):
        """测试检测不同内容的规则-有冲突"""
        local_rule = RuleVersion(
            version_id="v1",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_1",
            timestamp=datetime.now().isoformat(),
            content={"action": "allow"},
            effectiveness_score=80.0,
            status="published"
        )

        community_rule = RuleVersion(
            version_id="v2",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_2",
            timestamp=datetime.now().isoformat(),
            content={"action": "deny"},
            effectiveness_score=85.0,
            status="published"
        )

        assert ConflictResolver.detect_conflicts(local_rule, community_rule)

    def test_resolve_local_priority(self):
        """测试本地优先冲突解决"""
        local_rule = RuleVersion(
            version_id="v1",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_1",
            timestamp=datetime.now().isoformat(),
            content={"action": "allow"},
            effectiveness_score=80.0,
            status="published"
        )

        community_rule = RuleVersion(
            version_id="v2",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_2",
            timestamp=datetime.now().isoformat(),
            content={"action": "deny"},
            effectiveness_score=85.0,
            status="published"
        )

        conflict = RuleConflict(
            conflict_id="c1",
            local_rule=local_rule,
            community_rule=community_rule,
            detected_at=datetime.now().isoformat(),
            resolution_strategy=ConflictResolution.LOCAL_PRIORITY
        )

        resolved = ConflictResolver.resolve_conflict(conflict)
        assert resolved.version_id == "v1"
        assert resolved.content["action"] == "allow"

    def test_resolve_community_priority(self):
        """测试社群优先冲突解决"""
        local_rule = RuleVersion(
            version_id="v1",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_1",
            timestamp=datetime.now().isoformat(),
            content={"action": "allow"},
            effectiveness_score=80.0,
            status="published"
        )

        community_rule = RuleVersion(
            version_id="v2",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_2",
            timestamp=datetime.now().isoformat(),
            content={"action": "deny"},
            effectiveness_score=85.0,
            status="published"
        )

        conflict = RuleConflict(
            conflict_id="c1",
            local_rule=local_rule,
            community_rule=community_rule,
            detected_at=datetime.now().isoformat(),
            resolution_strategy=ConflictResolution.COMMUNITY_PRIORITY
        )

        resolved = ConflictResolver.resolve_conflict(conflict)
        assert resolved.version_id == "v2"
        assert resolved.content["action"] == "deny"

    def test_resolve_merge(self):
        """测试合并冲突解决"""
        local_rule = RuleVersion(
            version_id="v1",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_1",
            timestamp=datetime.now().isoformat(),
            content={"action": "allow", "timeout": 10},
            effectiveness_score=80.0,
            status="published"
        )

        community_rule = RuleVersion(
            version_id="v2",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_2",
            timestamp=datetime.now().isoformat(),
            content={"action": "deny", "priority": "high"},
            effectiveness_score=85.0,
            status="published"
        )

        conflict = RuleConflict(
            conflict_id="c1",
            local_rule=local_rule,
            community_rule=community_rule,
            detected_at=datetime.now().isoformat(),
            resolution_strategy=ConflictResolution.MERGE
        )

        resolved = ConflictResolver.resolve_conflict(conflict)
        # 合并后应包含社群版本的内容（覆盖）
        assert resolved.content["action"] == "deny"
        assert resolved.content["priority"] == "high"

    def test_resolve_version(self):
        """测试版本管理冲突解决"""
        local_rule = RuleVersion(
            version_id="v1",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_1",
            timestamp=datetime.now().isoformat(),
            content={"action": "allow"},
            effectiveness_score=60.0,
            status="published"
        )

        community_rule = RuleVersion(
            version_id="v2",
            rule_id="rule_123",
            parent_version=None,
            author_agent="agent_2",
            timestamp=datetime.now().isoformat(),
            content={"action": "deny"},
            effectiveness_score=85.0,
            status="published"
        )

        conflict = RuleConflict(
            conflict_id="c1",
            local_rule=local_rule,
            community_rule=community_rule,
            detected_at=datetime.now().isoformat(),
            resolution_strategy=ConflictResolution.VERSION
        )

        resolved = ConflictResolver.resolve_conflict(conflict)
        # 应选择效能分数更高的版本
        assert resolved.version_id == "v2"


class TestCommunityLeaderboard:
    """社群排行榜测试"""

    def test_init(self):
        """测试初始化"""
        board = CommunityLeaderboard()
        assert board.rules == {}
        assert board.rankings == []

    def test_add_rule(self):
        """测试添加规则"""
        board = CommunityLeaderboard()
        rule = CommunityRule(
            rule_id="rule_1",
            versions=[],
            effectiveness_history=[
                (datetime.now().isoformat(), 85.0),
                (datetime.now().isoformat(), 88.0)
            ],
            adoption_count=10,
            project_tags={"security"}
        )

        board.add_rule(rule)
        assert "rule_1" in board.rules

    def test_update_effectiveness(self):
        """测试更新效能并刷新排行"""
        board = CommunityLeaderboard()
        rule = CommunityRule(
            rule_id="rule_1",
            versions=[],
            effectiveness_history=[],
            adoption_count=0,
            project_tags=set()
        )

        board.add_rule(rule)
        board.update_effectiveness("rule_1", 82.5)

        assert len(board.rules["rule_1"].effectiveness_history) == 1
        assert board.rules["rule_1"].leaderboard_score == 82.5

    def test_record_adoption(self):
        """测试记录规则采纳"""
        board = CommunityLeaderboard()
        rule = CommunityRule(rule_id="rule_1", versions=[], effectiveness_history=[], adoption_count=0)
        board.add_rule(rule)

        board.record_adoption("rule_1")
        board.record_adoption("rule_1")

        assert board.rules["rule_1"].adoption_count == 2

    def test_refresh_rankings(self):
        """测试刷新排行榜"""
        board = CommunityLeaderboard()

        rule1 = CommunityRule(rule_id="rule_1", versions=[], effectiveness_history=[], adoption_count=0)
        rule1.leaderboard_score = 90.0
        rule2 = CommunityRule(rule_id="rule_2", versions=[], effectiveness_history=[], adoption_count=0)
        rule2.leaderboard_score = 75.0
        rule3 = CommunityRule(rule_id="rule_3", versions=[], effectiveness_history=[], adoption_count=0)
        rule3.leaderboard_score = 85.0

        board.add_rule(rule1)
        board.add_rule(rule2)
        board.add_rule(rule3)
        board._refresh_rankings()

        # 排序应为 rule_1(90) > rule_3(85) > rule_2(75)
        assert board.rankings[0][0] == "rule_1"
        assert board.rankings[1][0] == "rule_3"
        assert board.rankings[2][0] == "rule_2"

        # 位置应正确更新
        assert board.rules["rule_1"].leaderboard_position == 1
        assert board.rules["rule_3"].leaderboard_position == 2
        assert board.rules["rule_2"].leaderboard_position == 3

    def test_get_top_rules(self):
        """测试获取排行前N的规则"""
        board = CommunityLeaderboard()

        for i in range(15):
            rule = CommunityRule(rule_id=f"rule_{i}", versions=[], effectiveness_history=[], adoption_count=0)
            rule.leaderboard_score = float(100 - i * 5)
            board.add_rule(rule)

        board._refresh_rankings()
        top_10 = board.get_top_rules(10)

        assert len(top_10) == 10
        assert top_10[0].rule_id == "rule_0"
        assert top_10[0].leaderboard_score == 100.0

    def test_get_leaderboard(self):
        """测试获取排行榜数据"""
        board = CommunityLeaderboard()

        rule = CommunityRule(rule_id="rule_1", versions=[], effectiveness_history=[], adoption_count=5)
        rule.leaderboard_score = 85.0
        board.add_rule(rule)
        board._refresh_rankings()

        leaderboard = board.get_leaderboard()

        assert len(leaderboard) == 1
        assert leaderboard[0]["rule_id"] == "rule_1"
        assert leaderboard[0]["score"] == 85.0
        assert leaderboard[0]["adoption_count"] == 5


class TestKnowledgeFederation:
    """知识联邦系统测试"""

    def test_init(self, fed):
        """测试初始化"""
        assert fed.workspace is not None
        assert fed.agent_id is not None
        assert fed.local_registry is not None
        assert fed.conflict_resolver is not None
        assert fed.leaderboard is not None

    def test_publish_rule(self, fed, temp_workspace):
        """测试发布规则"""
        version_id = fed.publish_rule(
            rule_id="security_rule",
            content={"check": "permission"},
            effectiveness=88.0,
            tags=["security", "critical"]
        )

        assert version_id is not None

        # 验证日志记录
        assert fed.federation_log.exists()
        with open(fed.federation_log, 'r') as f:
            records = [json.loads(line) for line in f]
            assert any(r["rule_id"] == "security_rule" for r in records)

    def test_subscribe_community_rules(self, fed):
        """测试订阅社群规则"""
        # 添加社群规则到排行榜
        rule = CommunityRule(
            rule_id="community_rule",
            versions=[],
            effectiveness_history=[],
            adoption_count=3,
            project_tags={"common"}
        )
        fed.leaderboard.add_rule(rule)

        # 订阅规则
        rules = fed.subscribe_community_rules()
        assert len(rules) >= 1
        assert any(r.rule_id == "community_rule" for r in rules)

    def test_integrate_community_rule_no_conflict(self, fed):
        """测试集成社群规则-无冲突"""
        # 创建社群规则
        version = RuleVersion(
            version_id="v1",
            rule_id="new_rule",
            parent_version=None,
            author_agent="agent_2",
            timestamp=datetime.now().isoformat(),
            content={"action": "check"},
            effectiveness_score=90.0,
            status="published"
        )

        community_rule = CommunityRule(
            rule_id="new_rule",
            versions=[version],
            effectiveness_history=[(datetime.now().isoformat(), 90.0)],
            adoption_count=0,
            project_tags={"test"}
        )

        # 集成
        result = fed.integrate_community_rule(community_rule)
        assert result.version_id == "v1"

    def test_integrate_community_rule_with_conflict(self, fed, temp_workspace):
        """测试集成社群规则-有冲突"""
        # 先注册本地规则
        fed.local_registry.register_rule(
            rule_id="conflict_rule",
            content={"action": "allow"},
            effectiveness=70.0
        )

        # 创建冲突的社群规则
        version = RuleVersion(
            version_id="v2",
            rule_id="conflict_rule",
            parent_version=None,
            author_agent="agent_2",
            timestamp=datetime.now().isoformat(),
            content={"action": "deny"},
            effectiveness_score=85.0,
            status="published"
        )

        community_rule = CommunityRule(
            rule_id="conflict_rule",
            versions=[version],
            effectiveness_history=[(datetime.now().isoformat(), 85.0)],
            adoption_count=0,
            project_tags={"test"}
        )

        # 集成（应触发冲突解决）
        result = fed.integrate_community_rule(community_rule)
        assert result is not None

        # 验证冲突日志
        assert fed.conflict_log.exists()
        with open(fed.conflict_log, 'r') as f:
            records = [json.loads(line) for line in f]
            assert len(records) > 0

    def test_get_rule_genealogy(self, fed):
        """测试获取规则演化历史"""
        # 注册一个规则
        version1 = fed.local_registry.register_rule(
            "genealogy_rule",
            {"version": 1},
            80.0
        )

        # 获取族谱
        genealogy = fed.get_rule_genealogy("genealogy_rule")
        assert len(genealogy) > 0
        assert genealogy[-1].rule_id == "genealogy_rule"

    def test_get_statistics(self, fed):
        """测试获取统计信息"""
        # 添加一些规则
        fed.local_registry.register_rule("rule_1", {}, 85.0)
        fed.publish_rule("rule_2", {"test": True}, 90.0)

        stats = fed.get_statistics()

        assert "agent_id" in stats
        assert "project_id" in stats
        assert "local_rules_count" in stats
        assert "community_rules_count" in stats
        assert "conflicts_detected" in stats
        assert "leaderboard_top_10" in stats


class TestIntegration:
    """集成测试"""

    def test_full_workflow(self, temp_workspace):
        """完整工作流测试"""
        fed = KnowledgeFederation(str(temp_workspace))

        # 1. 发布本地规则
        version_id = fed.publish_rule(
            "workflow_rule",
            {"condition": "x > 10"},
            85.0,
            ["test", "important"]
        )
        assert version_id is not None

        # 2. 创建社群规则
        rule_version = RuleVersion(
            version_id="v_community",
            rule_id="workflow_rule",
            parent_version=None,
            author_agent="community_agent",
            timestamp=datetime.now().isoformat(),
            content={"condition": "x > 10"},
            effectiveness_score=88.0,
            status="published"
        )

        community_rule = CommunityRule(
            rule_id="workflow_rule",
            versions=[rule_version],
            effectiveness_history=[(datetime.now().isoformat(), 88.0)],
            adoption_count=2,
            project_tags={"shared"}
        )

        # 3. 集成社群规则
        result = fed.integrate_community_rule(community_rule)
        assert result is not None

        # 4. 获取统计
        stats = fed.get_statistics()
        assert stats["local_rules_count"] > 0

    def test_conflict_resolution_workflow(self, temp_workspace):
        """冲突解决工作流"""
        fed = KnowledgeFederation(str(temp_workspace))

        # 1. 注册本地规则
        fed.publish_rule("conflict_test", {"action": "allow"}, 75.0)

        # 2. 创建不同的社群版本
        version = RuleVersion(
            version_id="v_community",
            rule_id="conflict_test",
            parent_version=None,
            author_agent="other_agent",
            timestamp=datetime.now().isoformat(),
            content={"action": "deny"},
            effectiveness_score=92.0,
            status="published"
        )

        community_rule = CommunityRule(
            rule_id="conflict_test",
            versions=[version],
            effectiveness_history=[(datetime.now().isoformat(), 92.0)],
            adoption_count=5,
            project_tags={"security"}
        )

        # 3. 集成（应解决冲突）
        result = fed.integrate_community_rule(community_rule)
        assert result is not None

        # 4. 验证冲突被记录
        conflicts = fed._count_conflicts()
        assert conflicts > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
