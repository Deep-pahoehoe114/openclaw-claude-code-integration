#!/usr/bin/env python3
"""
test_central_api.py - 中央知识库 API 测试
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

# 需要在导入前设置临时存储路径
import os
temp_storage = tempfile.mkdtemp()
os.environ["KNOWLEDGE_FEDERATION_STORAGE"] = temp_storage

from skills.knowledge_federation.scripts.central_api import (
    app, CentralStore, PublishRequest, RuleResponse, LeaderboardEntry
)


@pytest.fixture
def store():
    """创建测试存储"""
    test_dir = Path(temp_storage) / "test"
    return CentralStore(storage_dir=str(test_dir))


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestCentralStore:
    """中央存储测试"""

    def test_publish_rule(self, store):
        """测试规则发布"""
        req = PublishRequest(
            rule_id="test_rule",
            version_id="v1",
            author_agent="test_agent",
            content={"action": "test"},
            effectiveness_score=85.0,
            tags=["test"],
        )

        resp = store.publish_rule(req)

        assert resp.success is True
        assert resp.rule_id == "test_rule"
        assert resp.version_id == "v1"
        assert resp.leaderboard_position == 1

    def test_publish_multiple_rules(self, store):
        """测试发布多条规则"""
        for i in range(3):
            req = PublishRequest(
                rule_id=f"rule_{i}",
                version_id=f"v{i}",
                author_agent=f"agent_{i}",
                content={"action": f"test_{i}"},
                effectiveness_score=70.0 + i * 10,
                tags=["test"],
            )
            store.publish_rule(req)

        rules = store.get_rules()
        assert len(rules) == 3

    def test_get_rules_by_tags(self, store):
        """测试按标签过滤"""
        req1 = PublishRequest(
            rule_id="rule_security",
            version_id="v1",
            author_agent="agent_1",
            content={"action": "security_test"},
            effectiveness_score=85.0,
            tags=["security"],
        )
        req2 = PublishRequest(
            rule_id="rule_finance",
            version_id="v1",
            author_agent="agent_2",
            content={"action": "finance_test"},
            effectiveness_score=80.0,
            tags=["finance"],
        )

        store.publish_rule(req1)
        store.publish_rule(req2)

        security_rules = store.get_rules(tags=["security"])
        assert len(security_rules) == 1
        assert security_rules[0].rule_id == "rule_security"

    def test_get_rules_by_min_score(self, store):
        """测试按最低分数过滤"""
        for score in [60, 75, 90]:
            req = PublishRequest(
                rule_id=f"rule_{score}",
                version_id="v1",
                author_agent="agent",
                content={"score": score},
                effectiveness_score=score,
                tags=["test"],
            )
            store.publish_rule(req)

        filtered = store.get_rules(min_score=75)
        assert len(filtered) == 2
        assert all(r.effectiveness_score >= 75 for r in filtered)

    def test_leaderboard(self, store):
        """测试排行榜"""
        scores = [85, 92, 78, 95, 88]
        for i, score in enumerate(scores):
            req = PublishRequest(
                rule_id=f"rule_{i}",
                version_id="v1",
                author_agent="agent",
                content={"score": score},
                effectiveness_score=score,
                tags=["test"],
            )
            store.publish_rule(req)

        board = store.get_leaderboard(limit=3)

        assert len(board) == 3
        assert board[0].score == 95  # 最高分排第一
        assert board[1].score == 92
        assert board[2].score == 88

    def test_record_adoption(self, store):
        """测试采纳记录"""
        req = PublishRequest(
            rule_id="rule_to_adopt",
            version_id="v1",
            author_agent="agent",
            content={"action": "test"},
            effectiveness_score=85.0,
            tags=["test"],
        )
        store.publish_rule(req)

        # 记录采纳
        result = store.record_adoption("rule_to_adopt")
        assert result is True

        rules = store.get_rules()
        assert rules[0].adoption_count == 1

        # 重复采纳
        store.record_adoption("rule_to_adopt")
        assert rules[0].adoption_count == 2

    def test_resolve_conflict(self, store):
        """测试冲突解决"""
        local = {
            "rule_id": "conflict_rule",
            "version_id": "v1",
            "effectiveness_score": 70,
            "content": {"timeout": 10},
        }
        community = {
            "rule_id": "conflict_rule",
            "version_id": "v2",
            "effectiveness_score": 88,
            "content": {"timeout": 5, "cache": True},
        }

        # 测试本地优先
        result = store.resolve_conflict(local, community, "local_priority")
        assert result.conflict_detected is True
        assert result.strategy_used == "local_priority"

        # 测试社群优先
        result = store.resolve_conflict(local, community, "community_priority")
        assert result.strategy_used == "community_priority"

        # 测试合并
        result = store.resolve_conflict(local, community, "merge")
        assert result.strategy_used == "merge"

        # 测试版本（高分优先）
        result = store.resolve_conflict(local, community, "version")
        assert result.strategy_used == "version"

    def test_statistics(self, store):
        """测试统计信息"""
        for i in range(3):
            req = PublishRequest(
                rule_id=f"rule_{i}",
                version_id="v1",
                author_agent=f"agent_{i}",
                content={"action": f"test_{i}"},
                effectiveness_score=80.0,
                tags=["test"],
            )
            store.publish_rule(req)

        stats = store.get_statistics()

        assert stats.total_rules == 3
        assert stats.total_agents == 3
        assert stats.total_adoptions == 0


class TestCentralAPI:
    """中央 API 路由测试"""

    def test_root(self, client):
        """测试根路由"""
        resp = client.get("/")
        assert resp.status_code == 200
        assert "version" in resp.json()

    def test_health(self, client):
        """测试健康检查"""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_publish_rule(self, client):
        """测试发布规则"""
        resp = client.post("/federation/publish", json={
            "rule_id": "api_test_rule",
            "version_id": "v1",
            "author_agent": "test_client",
            "content": {"action": "test"},
            "effectiveness_score": 85.0,
            "tags": ["test"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["rule_id"] == "api_test_rule"

    def test_get_rules(self, client):
        """测试获取规则列表"""
        # 先发布一条规则
        client.post("/federation/publish", json={
            "rule_id": "list_test",
            "version_id": "v1",
            "author_agent": "test",
            "content": {},
            "effectiveness_score": 80.0,
            "tags": ["test"],
        })

        resp = client.get("/federation/rules")
        assert resp.status_code == 200
        rules = resp.json()
        assert isinstance(rules, list)
        assert len(rules) >= 1

    def test_get_leaderboard(self, client):
        """测试排行榜"""
        resp = client.get("/federation/leaderboard")
        assert resp.status_code == 200
        board = resp.json()
        assert isinstance(board, list)

    def test_subscribe_rules(self, client):
        """测试订阅规则"""
        resp = client.get("/federation/subscribe?min_score=50")
        assert resp.status_code == 200
        rules = resp.json()
        assert isinstance(rules, list)

    def test_get_stats(self, client):
        """测试统计接口"""
        resp = client.get("/federation/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert "total_rules" in stats
        assert "total_agents" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])