#!/usr/bin/env python3
"""
test_hook_integration.py - 钩子集成测试
"""

import pytest
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta

from skills.knowledge_federation.scripts.hook_integration import (
    HookDispatcher, HookType, HookContext,
    ToolDispatchContext, ToolResultContext,
    ToolDispatchHookHandler, ToolResultHookHandler,
    generate_hook_config, generate_hook_script,
)


class TestHookDispatcher:
    """钩子调度器测试"""

    def test_register_handler(self):
        """测试处理器注册"""
        dispatcher = HookDispatcher()

        class TestHandler(ToolDispatchHookHandler):
            pass

        handler = TestHandler()
        dispatcher.register(HookType.TOOL_DISPATCH, handler)

        stats = dispatcher.get_statistics()
        assert stats["handlers"]["agent:tool_dispatch"] == 1

    def test_dispatch(self):
        """测试钩子调度"""
        dispatcher = HookDispatcher()

        class TestHandler(ToolDispatchHookHandler):
            async def pre_hook(self, context):
                return {"processed": True, "tool": context.tool_name}

        handler = TestHandler()
        dispatcher.register(HookType.TOOL_DISPATCH, handler)

        context = ToolDispatchContext(
            session_id="test_session",
            agent_id="test_agent",
            timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
            tool_name="bash",
            tool_args={"command": "ls"},
        )

        result = asyncio.run(dispatcher.dispatch(HookType.TOOL_DISPATCH, context))

        assert result is not None
        assert result["processed"] is True
        assert result["tool"] == "bash"

    def test_dispatch_post(self):
        """测试后置钩子"""
        dispatcher = HookDispatcher()
        post_called = []

        class TestHandler(ToolResultHookHandler):
            async def post_hook(self, context, result=None):
                post_called.append(context.tool_name)

        handler = TestHandler()
        dispatcher.register(HookType.TOOL_RESULT, handler)

        context = ToolResultContext(
            session_id="test_session",
            agent_id="test_agent",
            timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
            tool_name="bash",
            tool_args={"command": "ls"},
            success=True,
            duration_ms=50.0,
        )

        asyncio.run(dispatcher.dispatch_post(HookType.TOOL_RESULT, context))

        assert len(post_called) == 1
        assert post_called[0] == "bash"

    def test_multiple_handlers(self):
        """测试多个处理器"""
        dispatcher = HookDispatcher()

        class Handler1(ToolDispatchHookHandler):
            async def pre_hook(self, context):
                return {"handler": 1}

        class Handler2(ToolDispatchHookHandler):
            async def pre_hook(self, context):
                return {"handler": 2}

        dispatcher.register(HookType.TOOL_DISPATCH, Handler1())
        dispatcher.register(HookType.TOOL_DISPATCH, Handler2())

        context = ToolDispatchContext(
            session_id="test_session",
            agent_id="test_agent",
            timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
            tool_name="test",
            tool_args={},
        )

        # 按优先级排序，后者返回
        result = asyncio.run(dispatcher.dispatch(HookType.TOOL_DISPATCH, context))

        # 后注册的高优先级处理器生效
        assert result["handler"] == 2


class TestToolDispatchContext:
    """工具调用上下文测试"""

    def test_create_context(self):
        """测试创建上下文"""
        context = ToolDispatchContext(
            session_id="session_123",
            agent_id="agent_abc",
            timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
            tool_name="bash",
            tool_args={"command": "ls -la"},
            fusion_score=85.0,
            rule_score=80.0,
            permission_score=75.0,
            final_decision="auto_allow",
        )

        assert context.session_id == "session_123"
        assert context.tool_name == "bash"
        assert context.fusion_score == 85.0
        assert context.final_decision == "auto_allow"


class TestToolResultContext:
    """工具结果上下文测试"""

    def test_create_context(self):
        """测试创建上下文"""
        context = ToolResultContext(
            session_id="session_123",
            agent_id="agent_abc",
            timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
            tool_name="bash",
            tool_args={"command": "ls"},
            success=True,
            duration_ms=45.0,
            user_satisfaction=4.5,
        )

        assert context.success is True
        assert context.duration_ms == 45.0
        assert context.user_satisfaction == 4.5


class TestHookConfig:
    """钩子配置测试"""

    def test_generate_hook_config(self):
        """测试生成钩子配置"""
        config = generate_hook_config(central_api="http://localhost:8000")

        assert config["version"] == "2.0.0"
        assert "hooks" in config
        assert "agent:tool_dispatch" in config["hooks"]
        assert "agent:tool_result" in config["hooks"]
        assert config["environment"]["KNOWLEDGE_FEDERATION_API"] == "http://localhost:8000"

    def test_generate_hook_script(self, tmp_path):
        """测试生成钩子脚本"""
        output_path = tmp_path / "test_hook.py"
        generate_hook_script(HookType.TOOL_DISPATCH, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "tool_dispatch" in content
        assert "HookDispatcher" in content


class TestHookHandler:
    """钩子处理器基类测试"""

    def test_priority(self):
        """测试优先级"""
        class HighPriority(ToolDispatchHookHandler):
            pass

        class LowPriority(ToolDispatchHookHandler):
            pass

        high = HighPriority(priority=100)
        low = LowPriority(priority=50)

        assert high.priority == 100
        assert low.priority == 50

    def test_enabled_default(self):
        """测试默认启用"""
        handler = ToolDispatchHookHandler()
        assert handler.enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])