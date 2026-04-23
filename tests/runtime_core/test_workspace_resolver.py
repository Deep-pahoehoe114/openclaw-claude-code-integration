from pathlib import Path

from oeck.runtime_core.session import SessionResolver
from oeck.runtime_core.workspace import WorkspaceResolver


def test_workspace_resolver_honors_explicit_workspace(tmp_path):
    resolver = WorkspaceResolver.from_workspace(tmp_path)

    assert resolver.layout.workspace_root == tmp_path.resolve()
    assert resolver.local_rules_dir() == tmp_path / ".local-rules"
    assert resolver.recovery_state_dir() == tmp_path / ".recovery"


def test_session_resolver_reads_explicit_transcript(tmp_path):
    workspace = WorkspaceResolver.from_workspace(tmp_path)
    sessions_dir = tmp_path / ".sessions"
    sessions_dir.mkdir()
    transcript = sessions_dir / "sample.jsonl"
    transcript.write_text('{"role":"user","content":"hi"}\n{"role":"assistant","content":"ok"}\n', encoding="utf-8")

    resolver = SessionResolver(workspace, session_dir=sessions_dir)
    messages = resolver.load_messages(limit=10)

    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
