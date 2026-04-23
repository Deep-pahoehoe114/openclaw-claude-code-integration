import subprocess
from pathlib import Path

from oeck.distribution import render_generated_docs
from oeck.runtime_core.workspace import WorkspaceResolver


def test_sync_repo_state_check_passes():
    subprocess.run(["python3", "tools/sync_repo_state.py"], check=True)
    result = subprocess.run(["python3", "tools/sync_repo_state.py", "--check"], check=False)

    assert result.returncode == 0


def test_render_generated_docs_supports_chinese_locale():
    resolver = WorkspaceResolver.from_workspace(Path.cwd())
    generated = render_generated_docs(resolver, locale="zh-CN")

    assert "会话健康分析与异常检测。" in generated["skills_section"]
    assert "OpenClaw 原生插件元数据与 bundle 产物。" in generated["adapters_section"]
