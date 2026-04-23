"""Validation pipeline and markdown-based checks."""

from __future__ import annotations

import fnmatch
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class CheckDefinition:
    name: str
    description: str
    commands: list[str]
    triggers: list[str]
    path: Path


def load_checks(checks_dir: Path) -> list[CheckDefinition]:
    checks = []
    for path in sorted(checks_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("+++"):
            continue
        _, frontmatter, _ = text.split("+++", 2)
        data = tomllib.loads(frontmatter)
        checks.append(
            CheckDefinition(
                name=data["name"],
                description=data.get("description", ""),
                commands=list(data.get("commands", [])),
                triggers=list(data.get("triggers", [])),
                path=path,
            )
        )
    return checks


def select_checks(checks: Iterable[CheckDefinition], changed_files: list[str] | None = None) -> list[CheckDefinition]:
    if not changed_files:
        return list(checks)
    selected = []
    for check in checks:
        if not check.triggers:
            selected.append(check)
            continue
        for changed in changed_files:
            if any(fnmatch.fnmatch(changed, pattern) for pattern in check.triggers):
                selected.append(check)
                break
    return selected


def run_check(check: CheckDefinition, cwd: Path) -> list[tuple[str, int]]:
    results = []
    for command in check.commands:
        completed = subprocess.run(command, cwd=cwd, shell=True, check=False)
        results.append((command, completed.returncode))
        if completed.returncode != 0:
            break
    return results
