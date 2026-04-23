"""Session transcript resolution."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Iterable, List

from .workspace import WorkspaceResolver


class SessionResolver:
    """Resolves session history across OpenClaw, Claude, and Codex layouts."""

    def __init__(self, resolver: WorkspaceResolver | None = None, session_dir: str | Path | None = None):
        self.resolver = resolver or WorkspaceResolver()
        self.explicit_session_dir = Path(session_dir).expanduser() if session_dir else None

    def candidate_dirs(self) -> List[Path]:
        config_session_dir = self.resolver.config.session_dir
        candidates = [
            self.explicit_session_dir,
            config_session_dir,
            self.resolver.layout.workspace_root / ".sessions",
            self.resolver.layout.sessions_state_dir,
            self.resolver.layout.legacy_sessions_dir,
            self.resolver.layout.workspace_root / ".codex" / "sessions",
            self.resolver.layout.workspace_root / ".claude" / "sessions",
        ]
        return [path for path in candidates if path]

    def iter_transcripts(self) -> Iterable[Path]:
        seen = set()
        for directory in self.candidate_dirs():
            if not directory or not directory.exists():
                continue
            for transcript in sorted(directory.glob("*.jsonl"), key=lambda item: item.stat().st_mtime, reverse=True):
                if transcript not in seen:
                    seen.add(transcript)
                    yield transcript

    def latest_transcript_path(self) -> Path | None:
        return next(self.iter_transcripts(), None)

    def load_messages(self, limit: int = 200) -> List[dict]:
        cli_messages = self._load_via_openclaw_cli(limit)
        if cli_messages:
            return cli_messages[-limit:]

        transcript_path = self.latest_transcript_path()
        if not transcript_path:
            return []

        messages: List[dict] = []
        for raw_line in transcript_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and obj.get("role") in {"user", "assistant"}:
                messages.append(obj)
                continue
            if isinstance(obj, dict) and obj.get("type") == "message":
                inner = obj.get("message", {})
                if isinstance(inner, dict) and inner.get("role") in {"user", "assistant"}:
                    messages.append(inner)
        return messages[-limit:]

    def _load_via_openclaw_cli(self, limit: int) -> List[dict]:
        try:
            result = subprocess.run(
                ["openclaw", "sessions", "history", "main", "--limit", str(limit), "--json"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except Exception:
            return []
        if result.returncode != 0 or not result.stdout.strip():
            return []
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []
        if isinstance(payload, dict) and isinstance(payload.get("messages"), list):
            return [item for item in payload["messages"] if isinstance(item, dict)]
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []
