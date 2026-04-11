#!/usr/bin/env python3
"""
hook_integration.py — OpenClaw 2.0 钩子系统集成

为 OpenClaw 2.0 Agent 提供钩子回调实现，支持：
- agent:tool_dispatch  - 工具调用前决策
- agent:tool_result    - 工具执行结果反馈
- session:start        - 会话开始
- session:end          - 会话结束

用法：
  python3 hook_integration.py --setup    # 生成钩子配置文件
  python3 hook_integration.py --check    # 检查钩子状态
  python3 hook_integration.py --test    # 测试钩子调用
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum

from skills.shared.logger import get_logger

logger = get_logger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# 钩子类型枚举
# ═══════════════════════════════════════════════════════════════════════════

class HookType(Enum):
    TOOL_DISPATCH = "agent:tool_dispatch"      # 工具调用前
    TOOL_RESULT = "agent:tool_result"         # 工具执行后
    SESSION_START = "session:start"            # 会话开始
    SESSION_END = "session:end"                # 会话结束
    RULE_EVALUATED = "rule:evaluated"         # 规则评估后
    MEMORY_STORED = "memory:stored"            # 记忆存储后


@dataclass
class HookContext:
    """钩子上下文"""
    session_id: str
    agent_id: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolDispatchContext(HookContext):
    """工具调用上下文"""
    tool_name: str = ""
    tool_args: Dict[str, Any] = field(default_factory=dict)
    fusion_score: float = 0.0
    rule_score: float = 0.0
    permission_score: float = 0.0
    final_decision: str = ""  # auto_allow, request_confirm, block


@dataclass
class ToolResultContext(HookContext):
    """工具执行结果上下文"""
    tool_name: str = ""
    tool_args: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    error: str = ""
    duration_ms: float = 0.0
    user_satisfaction: float = 0.0  # 1-5


# ═══════════════════════════════════════════════════════════════════════════
# 钩子处理器接口
# ═══════════════════════════════════════════════════════════════════════════

class HookHandler:
    """钩子处理器基类"""

    def __init__(self, priority: int = 100):
        self.priority = priority
        self.enabled = True

    async def pre_hook(self, context: HookContext) -> Optional[Dict]:
        """前置钩子（返回修改后的上下文或 None）"""
        return None

    async def post_hook(self, context: HookContext, result: Any = None) -> None:
        """后置钩子"""
        pass


class ToolDispatchHookHandler(HookHandler):
    """工具调用前钩子处理器"""

    def __init__(self, knowledge_fed=None, fusion_engine=None, rule_optimizer=None):
        super().__init__(priority=100)
        self.knowledge_fed = knowledge_fed
        self.fusion_engine = fusion_engine
        self.rule_optimizer = rule_optimizer

    async def pre_hook(self, context: ToolDispatchContext) -> Optional[Dict]:
        """工具调用决策"""
        decisions = []

        # 1. 获取适用的社群规则
        if self.knowledge_fed:
            try:
                community_rules = self.knowledge_fed.subscribe_community_rules(
                    filters={"min_score": 75}
                )
                if community_rules:
                    decisions.append({
                        "source": "community_rules",
                        "count": len(community_rules),
                        "top_score": community_rules[0].leaderboard_score if community_rules else 0,
                    })
            except Exception as e:
                logger.warning(f"获取社群规则失败: {e}")

        # 2. 评估本地规则
        if self.rule_optimizer:
            try:
                # 规则效能评估
                pass
            except Exception as e:
                logger.warning(f"评估本地规则失败: {e}")

        return {
            "hook": "tool_dispatch",
            "session_id": context.session_id,
            "tool_name": context.tool_name,
            "decisions": decisions,
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        }


class ToolResultHookHandler(HookHandler):
    """工具执行结果钩子处理器"""

    def __init__(self, knowledge_fed=None, rule_optimizer=None):
        super().__init__(priority=100)
        self.knowledge_fed = knowledge_fed
        self.rule_optimizer = rule_optimizer

    async def post_hook(self, context: ToolResultContext, result: Any = None) -> None:
        """处理工具执行结果"""
        # 1. 记录规则应用结果
        if self.rule_optimizer and context.success:
            try:
                self.rule_optimizer.record_rule_application(
                    rule_id=f"tool_{context.tool_name}",
                    fixed=True,
                    satisfaction=context.user_satisfaction or 3.0,
                )
            except Exception as e:
                logger.warning(f"记录规则应用失败: {e}")

        # 2. 发布高效能规则到社群
        if self.knowledge_fed and context.success and context.user_satisfaction >= 4.5:
            try:
                # 检查是否需要发布
                pass
            except Exception as e:
                logger.warning(f"发布规则失败: {e}")

        # 3. 记录失败模式
        if not context.success:
            try:
                logger.warning(f"工具执行失败: {context.tool_name} - {context.error}")
            except Exception:
                pass


class SessionEndHookHandler(HookHandler):
    """会话结束钩子处理器"""

    def __init__(self, knowledge_fed=None):
        super().__init__(priority=50)
        self.knowledge_fed = knowledge_fed

    async def post_hook(self, context: HookContext, result: Any = None) -> None:
        """会话结束后的处理"""
        if not self.knowledge_fed:
            return

        try:
            # 统计本会话发布的规则
            stats = self.knowledge_fed.get_statistics()
            logger.info(
                f"会话 {context.session_id} 结束 - "
                f"本地规则: {stats.get('local_rules_count', 0)}, "
                f"社群规则: {stats.get('community_rules_count', 0)}"
            )
        except Exception as e:
            logger.warning(f"会话结束处理失败: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 钩子调度器
# ═══════════════════════════════════════════════════════════════════════════

class HookDispatcher:
    """钩子调度器"""

    def __init__(self):
        self.handlers: Dict[HookType, List[HookHandler]] = {
            HookType.TOOL_DISPATCH: [],
            HookType.TOOL_RESULT: [],
            HookType.SESSION_START: [],
            HookType.SESSION_END: [],
            HookType.RULE_EVALUATED: [],
            HookType.MEMORY_STORED: [],
        }
        self.call_log: List[Dict] = []

    def register(self, hook_type: HookType, handler: HookHandler) -> None:
        """注册钩子处理器"""
        self.handlers[hook_type].append(handler)
        # 按优先级排序
        self.handlers[hook_type].sort(key=lambda h: h.priority, reverse=True)
        logger.info(f"注册钩子处理器: {hook_type.value} -> {type(handler).__name__}")

    def unregister(self, hook_type: HookType, handler: HookHandler) -> None:
        """注销钩子处理器"""
        if handler in self.handlers[hook_type]:
            self.handlers[hook_type].remove(handler)
            logger.info(f"注销钩子处理器: {hook_type.value} -> {type(handler).__name__}")

    async def dispatch(self, hook_type: HookType,
                       context: HookContext) -> Optional[Dict]:
        """调度钩子"""
        handlers = self.handlers.get(hook_type, [])
        if not handlers:
            return None

        result = None
        for handler in handlers:
            if not handler.enabled:
                continue

            try:
                hook_result = await handler.pre_hook(context)
                if hook_result:
                    result = hook_result
            except Exception as e:
                logger.error(f"钩子 {hook_type.value} 执行失败: {e}")

        # 记录调用
        self.call_log.append({
            "hook_type": hook_type.value,
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "session_id": context.session_id,
        })

        return result

    async def dispatch_post(self, hook_type: HookType,
                            context: HookContext,
                            result: Any = None) -> None:
        """调度后置钩子"""
        handlers = self.handlers.get(hook_type, [])
        for handler in handlers:
            if not handler.enabled:
                continue

            try:
                await handler.post_hook(context, result)
            except Exception as e:
                logger.error(f"后置钩子 {hook_type.value} 执行失败: {e}")

    def get_statistics(self) -> Dict:
        """获取钩子调用统计"""
        return {
            "total_calls": len(self.call_log),
            "by_type": self._count_by_type(),
            "handlers": self._count_handlers(),
        }

    def _count_by_type(self) -> Dict[str, int]:
        counts = {}
        for log in self.call_log:
            t = log["hook_type"]
            counts[t] = counts.get(t, 0) + 1
        return counts

    def _count_handlers(self) -> Dict[str, int]:
        return {ht.value: len(hs) for ht, hs in self.handlers.items()}


# ═══════════════════════════════════════════════════════════════════════════
# OpenClaw 2.0 钩子配置生成器
# ═══════════════════════════════════════════════════════════════════════════

def generate_hook_config(central_api: str = None) -> Dict:
    """生成 OpenClaw 钩子配置文件"""

    workspace = Path.home() / ".openclaw" / "workspace"
    hook_dir = workspace / ".hooks"
    hook_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "version": "2.0.0",
        "hooks": {
            "agent:tool_dispatch": {
                "enabled": True,
                "script": str(hook_dir / "tool_dispatch.py"),
                "timeout_ms": 100,
            },
            "agent:tool_result": {
                "enabled": True,
                "script": str(hook_dir / "tool_result.py"),
                "timeout_ms": 200,
            },
            "session:start": {
                "enabled": True,
                "script": str(hook_dir / "session_start.py"),
                "timeout_ms": 50,
            },
            "session:end": {
                "enabled": True,
                "script": str(hook_dir / "session_end.py"),
                "timeout_ms": 100,
            },
        },
        "environment": {
            "KNOWLEDGE_FEDERATION_API": central_api or "",
            "HOOK_LOG_DIR": str(workspace / ".hook-logs"),
        },
    }

    return config


def generate_hook_script(hook_type: HookType, output_path: Path) -> None:
    """生成钩子脚本文件"""

    if hook_type == HookType.TOOL_DISPATCH:
        content = '''#!/usr/bin/env python3
"""tool_dispatch.py - OpenClaw agent:tool_dispatch hook"""

import json
import sys
from pathlib import Path

# 添加 skills 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.knowledge_federation.scripts.hook_integration import (
    HookDispatcher, ToolDispatchHookHandler, ToolDispatchContext
)
from skills.fusion_engine.scripts.fusion_engine import MultiSourceFusionEngine
from skills.rule_optimizer.scripts.rule_optimizer import RuleOptimizer
from skills.knowledge_federation.scripts.knowledge_federation import KnowledgeFederation
from datetime import datetime, timezone, timedelta

async def main():
    data = json.loads(sys.stdin.read())
    session_id = data.get("session_id", "unknown")
    tool_name = data.get("tool_name", "")
    tool_args = data.get("args", {})

    # 初始化组件
    workspace = Path.home() / ".openclaw" / "workspace"
    central_api = data.get("KNOWLEDGE_FEDERATION_API")

    fusion = MultiSourceFusionEngine()
    optimizer = RuleOptimizer()
    fed = KnowledgeFederation(workspace_dir=str(workspace), central_api=central_api)

    # 创建调度器
    dispatcher = HookDispatcher()
    dispatcher.register(
        "agent:tool_dispatch",
        ToolDispatchHookHandler(
            knowledge_fed=fed,
            fusion_engine=fusion,
            rule_optimizer=optimizer,
        )
    )

    # 构建上下文
    context = ToolDispatchContext(
        session_id=session_id,
        agent_id=data.get("agent_id", "unknown"),
        timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        tool_name=tool_name,
        tool_args=tool_args,
        metadata=data,
    )

    # 执行钩子
    result = await dispatcher.dispatch("agent:tool_dispatch", context)

    # 输出结果
    print(json.dumps(result or {}, ensure_ascii=False))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''
    elif hook_type == HookType.TOOL_RESULT:
        content = '''#!/usr/bin/env python3
"""tool_result.py - OpenClaw agent:tool_result hook"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.knowledge_federation.scripts.hook_integration import (
    HookDispatcher, ToolResultHookHandler, ToolResultContext
)
from skills.knowledge_federation.scripts.knowledge_federation import KnowledgeFederation
from datetime import datetime, timezone, timedelta

async def main():
    data = json.loads(sys.stdin.read())
    session_id = data.get("session_id", "unknown")
    tool_name = data.get("tool_name", "")
    tool_args = data.get("args", {})
    success = data.get("success", False)
    error = data.get("error", "")
    duration_ms = data.get("duration_ms", 0)

    workspace = Path.home() / ".openclaw" / "workspace"
    central_api = data.get("KNOWLEDGE_FEDERATION_API")

    fed = KnowledgeFederation(workspace_dir=str(workspace), central_api=central_api)

    dispatcher = HookDispatcher()
    dispatcher.register(
        "agent:tool_result",
        ToolResultHookHandler(knowledge_fed=fed)
    )

    context = ToolResultContext(
        session_id=session_id,
        agent_id=data.get("agent_id", "unknown"),
        timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        tool_name=tool_name,
        tool_args=tool_args,
        success=success,
        error=error,
        duration_ms=duration_ms,
        user_satisfaction=data.get("user_satisfaction", 3.0),
    )

    await dispatcher.dispatch_post("agent:tool_result", context)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''
    elif hook_type == HookType.SESSION_END:
        content = '''#!/usr/bin/env python3
"""session_end.py - OpenClaw session:end hook"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.knowledge_federation.scripts.knowledge_federation import KnowledgeFederation
from datetime import datetime, timezone, timedelta

def main():
    data = json.loads(sys.stdin.read())
    session_id = data.get("session_id", "unknown")

    workspace = Path.home() / ".openclaw" / "workspace"
    central_api = data.get("KNOWLEDGE_FEDERATION_API")

    fed = KnowledgeFederation(workspace_dir=str(workspace), central_api=central_api)
    stats = fed.get_statistics()

    print(json.dumps({
        "session_id": session_id,
        "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "federation_stats": stats,
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()
'''
    else:
        content = f'''#!/usr/bin/env python3
"""hook_{hook_type.value.replace(":", "_")}.py - OpenClaw {hook_type.value} hook"""
import json
import sys

def main():
    data = json.loads(sys.stdin.read())
    print(json.dumps({{"status": "ok", "hook": "{hook_type.value}"}}, ensure_ascii=False))

if __name__ == "__main__":
    main()
'''

    output_path.write_text(content)
    output_path.chmod(0o755)


# ═══════════════════════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════════════════════

def main():
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw 2.0 钩子集成")
    parser.add_argument("--setup", action="store_true", help="生成钩子配置文件")
    parser.add_argument("--check", action="store_true", help="检查钩子状态")
    parser.add_argument("--test", action="store_true", help="测试钩子调用")
    parser.add_argument("--central-api", help="中央API地址")
    args = parser.parse_args()

    if args.setup:
        workspace = Path.home() / ".openclaw" / "workspace"
        hook_dir = workspace / ".hooks"
        hook_dir.mkdir(parents=True, exist_ok=True)

        # 生成配置
        config = generate_hook_config(args.central_api)
        config_file = hook_dir / "config.json"
        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))
        print(f"✅ 钩子配置已生成: {config_file}")

        # 生成钩子脚本
        for hook_type in [HookType.TOOL_DISPATCH, HookType.TOOL_RESULT, HookType.SESSION_END]:
            script_path = hook_dir / f"{hook_type.value.replace(':', '_')}.py"
            generate_hook_script(hook_type, script_path)
            print(f"✅ 钩子脚本已生成: {script_path}")

        print("\n📝 下一步:")
        print("1. 编辑 .hooks/config.json 设置 KNOWLEDGE_FEDERATION_API")
        print("2. 重启 OpenClaw agent")
        print("3. 使用 --check 验证钩子状态")

    elif args.check:
        workspace = Path.home() / ".openclaw" / "workspace"
        hook_dir = workspace / ".hooks"
        config_file = hook_dir / "config.json"

        if not config_file.exists():
            print("❌ 钩子未配置，请先运行 --setup")
            sys.exit(1)

        config = json.loads(config_file.read_text())
        print("✅ 钩子配置:")
        print(json.dumps(config, indent=2, ensure_ascii=False))

    elif args.test:
        print("🧪 测试钩子调用...")
        # 简单的测试
        dispatcher = HookDispatcher()
        dispatcher.register(
            HookType.TOOL_DISPATCH,
            ToolDispatchHookHandler()
        )
        dispatcher.register(
            HookType.TOOL_RESULT,
            ToolResultHookHandler()
        )

        import asyncio

        async def run_test():
            # 测试 tool_dispatch
            context = ToolDispatchContext(
                session_id="test_session",
                agent_id="test_agent",
                timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                tool_name="bash",
                tool_args={"command": "ls"},
            )
            result = await dispatcher.dispatch(HookType.TOOL_DISPATCH, context)
            print(f"✅ tool_dispatch 结果: {result}")

            # 测试 tool_result
            result_context = ToolResultContext(
                session_id="test_session",
                agent_id="test_agent",
                timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                tool_name="bash",
                tool_args={"command": "ls"},
                success=True,
                duration_ms=50.0,
            )
            await dispatcher.dispatch_post(HookType.TOOL_RESULT, result_context)
            print("✅ tool_result 执行完成")

            print(f"📊 钩子统计: {dispatcher.get_statistics()}")

        asyncio.run(run_test())

    else:
        parser.print_help()


if __name__ == "__main__":
    main()