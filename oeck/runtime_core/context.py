"""Context engine and repo mapping."""

from __future__ import annotations

from pathlib import Path

from .workspace import WorkspaceResolver


class ContextEngine:
    def __init__(self, resolver: WorkspaceResolver | None = None):
        self.resolver = resolver or WorkspaceResolver()

    def repo_map(self, max_entries: int = 40) -> dict:
        root = self.resolver.layout.workspace_root
        entries = []
        for path in sorted(root.rglob("*")):
            if path.is_dir():
                continue
            relative = path.relative_to(root)
            if relative.parts and relative.parts[0] in {".git", ".pytest_cache", "__pycache__"}:
                continue
            entries.append(str(relative))
            if len(entries) >= max_entries:
                break
        return {
            "root": str(root),
            "files": entries,
            "skills": [path.name for path in sorted(self.resolver.layout.skills_dir.iterdir()) if path.is_dir()],
        }

    def codebase_summary(self) -> dict:
        repo_map = self.repo_map()
        return {
            "root": repo_map["root"],
            "skill_count": len(repo_map["skills"]),
            "top_files": repo_map["files"][:15],
        }
