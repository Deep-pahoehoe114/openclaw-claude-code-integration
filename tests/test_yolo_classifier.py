"""
test_yolo_classifier.py — Tests for yolo_classifier.py (tool risk classification)

Covers:
- LOW risk for read-only tools
- MEDIUM risk for write/edit operations
- HIGH risk for delete/destructive operations
- HIGH risk for external communication tools
- bash command pattern matching
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).parent.parent / "skills" / "yolo-permissions" / "scripts"),
)
from yolo_classifier import quick_rule_check, classify


class TestLowRiskTools:
    """Tools that should always be LOW risk."""

    @pytest.mark.parametrize(
        "tool",
        [
            "read",
            "search",
            "memory_recall",
            "web_search",
            "glob",
            "grep",
            "pwd",
            "whoami",
            "hostname",
        ],
    )
    def test_read_only_tools(self, tool):
        result = quick_rule_check(tool, {})
        assert result is not None
        assert result["risk"] == "LOW"
        assert result["action"] == "allow"


class TestHighRiskTools:
    """Tools that should always require confirmation."""

    @pytest.mark.parametrize(
        "tool",
        [
            "delete",
            "trash",
            "shutdown",
            "reboot",
        ],
    )
    def test_delete_tools(self, tool):
        result = quick_rule_check(tool, {})
        assert result is not None
        assert result["risk"] == "HIGH"
        assert result["action"] == "confirm"


class TestBashPatterns:
    """Bash command pattern classification."""

    def test_safe_bash_ls(self):
        result = quick_rule_check("bash", {"command": "ls -la"})
        assert result is not None
        assert result["risk"] == "LOW"

    def test_safe_bash_git_status(self):
        result = quick_rule_check("bash", {"command": "git status"})
        assert result is not None
        assert result["risk"] == "LOW"

    def test_safe_bash_git_log(self):
        result = quick_rule_check("bash", {"command": "git log --oneline"})
        assert result is not None
        assert result["risk"] == "LOW"

    def test_safe_bash_ps(self):
        result = quick_rule_check("bash", {"command": "ps aux | grep python"})
        assert result is not None
        assert result["risk"] == "LOW"

    def test_safe_bash_echo(self):
        result = quick_rule_check("bash", {"command": "echo $PATH"})
        # echo $PATH uses safe var PATH — passes
        assert result is not None
        assert result["risk"] == "LOW"

    def test_risky_bash_rm_rf(self):
        result = quick_rule_check("bash", {"command": "rm -rf /tmp/test"})
        assert result is not None
        assert result["risk"] == "HIGH"

    def test_risky_bash_chmod_777(self):
        result = quick_rule_check("bash", {"command": "chmod 777 /some/path"})
        assert result is not None
        assert result["risk"] == "HIGH"

    def test_risky_bash_git_force_push(self):
        result = quick_rule_check("bash", {"command": "git push --force origin main"})
        assert result is not None
        assert result["risk"] == "HIGH"

    def test_risky_bash_scp(self):
        result = quick_rule_check("bash", {"command": "scp file.txt user@host:/path"})
        assert result is not None
        assert result["risk"] == "HIGH"

    def test_risky_bash_dd(self):
        result = quick_rule_check("bash", {"command": "dd if=/dev/zero of=/tmp/out"})
        assert result is not None
        assert result["risk"] == "HIGH"

    def test_risky_bash_git_push(self):
        result = quick_rule_check("bash", {"command": "git push origin main"})
        assert result is not None
        assert result["risk"] == "HIGH"


class TestWriteEdit:
    """Write/edit tool path checking."""

    def test_write_user_dir(self):
        result = quick_rule_check("write", {"path": "~/test.txt"})
        assert result is not None
        assert result["risk"] == "MEDIUM"

    def test_write_openclaw_dir(self):
        result = quick_rule_check("write", {"path": "/Users/ybbms/.openclaw/test.txt"})
        assert result is not None
        assert result["risk"] == "HIGH"
        assert result["action"] == "block"

    def test_write_ssh_dir(self):
        result = quick_rule_check("edit", {"path": "/Users/ybbms/.ssh/config"})
        assert result is not None
        assert result["risk"] == "HIGH"

    def test_write_system_dir(self):
        result = quick_rule_check("write", {"path": "/etc/hosts"})
        assert result is not None
        assert result["risk"] == "HIGH"

    def test_write_credentials(self):
        result = quick_rule_check("write", {"path": "~/credentials.json"})
        assert result is not None
        assert result["risk"] == "HIGH"


class TestExternalComm:
    """External communication tools are HIGH risk."""

    @pytest.mark.parametrize(
        "tool",
        [
            "email",
            "webhook",
            "http_request",
            "send_message",
        ],
    )
    def test_external_tools_high_risk(self, tool):
        result = quick_rule_check(tool, {})
        assert result is not None
        assert result["risk"] == "HIGH"
        assert result["action"] == "confirm"


class TestClassifyFallback:
    """Classify falls back to AI for unknown tools without rules."""

    def test_unknown_tool_falls_through(self):
        # quick_rule_check returns None for unknown tools
        # classify() then calls AI — we just verify no crash
        result = classify("some_unknown_tool", {"param": "value"})
        # should return some result (AI or fallback)
        assert "risk" in result
        assert result["risk"] in ("LOW", "MEDIUM", "HIGH")
