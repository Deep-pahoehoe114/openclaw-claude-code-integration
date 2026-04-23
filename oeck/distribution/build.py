"""Manifest and generated documentation build helpers."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from oeck.adapters.distribution import ClaudeBundleAdapter, CodexBundleAdapter, OpenClawNativeAdapter
from oeck.runtime_core.workspace import WorkspaceResolver


def _count_tests(root: Path) -> tuple[int, list[str]]:
    total = 0
    inventory = []
    for path in sorted(list((root / "tests").rglob("test_*.py")) + list((root / "skills").rglob("test_*.py"))):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        file_total = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                file_total += 1
        if path.suffix == ".sh":
            file_total += 1
        total += file_total
        inventory.append(f"- `{path.relative_to(root)}`: {file_total}")
    shell_test = root / "tests" / "test_health_check.sh"
    if shell_test.exists():
        total += 1
        inventory.append(f"- `{shell_test.relative_to(root)}`: 1")
    return total, inventory


def _directory_tree(root: Path) -> str:
    interesting = [
        "metadata",
        "oeck",
        "skills",
        "docs",
        ".openclaw",
        ".claude-plugin",
        ".codex-plugin",
        "plugins",
        "tests",
        "tools",
        ".github",
    ]
    lines = []
    for name in interesting:
        path = root / name
        if not path.exists():
            continue
        lines.append(f"- `{name}/`")
        if path.is_dir():
            for child in sorted(path.iterdir()):
                if child.name in {"__pycache__", ".DS_Store"}:
                    continue
                lines.append(f"  - `{child.relative_to(root)}`")
    return "\n".join(lines)


def render_generated_docs(resolver: WorkspaceResolver | None = None) -> dict:
    resolver = resolver or WorkspaceResolver()
    root = resolver.layout.workspace_root
    metadata = json.loads((root / "metadata" / "canonical.json").read_text(encoding="utf-8"))
    skill_lines = [
        f"- `{item['id']}`: {item['summary']}"
        for item in metadata["skills"]
    ]
    test_total, test_inventory = _count_tests(root)
    generated = {
        "skills_count": len(metadata["skills"]),
        "tests_count": test_total,
        "skills_section": "\n".join(skill_lines),
        "tests_section": "\n".join(test_inventory),
        "tree_section": _directory_tree(root),
        "adapters_section": "\n".join(
            f"- `{item['id']}`: {item['summary']}" for item in metadata["adapters"]
        ),
    }
    docs_generated = root / "docs" / "generated"
    docs_generated.mkdir(parents=True, exist_ok=True)
    (docs_generated / "skills.md").write_text(generated["skills_section"] + "\n", encoding="utf-8")
    (docs_generated / "tests.md").write_text(generated["tests_section"] + "\n", encoding="utf-8")
    (docs_generated / "tree.md").write_text(generated["tree_section"] + "\n", encoding="utf-8")
    (docs_generated / "adapters.md").write_text(generated["adapters_section"] + "\n", encoding="utf-8")
    return generated


def build_distribution_assets(resolver: WorkspaceResolver | None = None) -> dict:
    resolver = resolver or WorkspaceResolver()
    root = resolver.layout.workspace_root
    payloads = {
        "openclaw": OpenClawNativeAdapter(resolver).build_manifest(),
        "claude": ClaudeBundleAdapter(resolver).build_manifest(),
        "codex": CodexBundleAdapter(resolver).build_manifest(),
    }
    (root / "openclaw.plugin.json").write_text(json.dumps(payloads["openclaw"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (root / ".codex-plugin").mkdir(parents=True, exist_ok=True)
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps(payloads["claude"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / ".codex-plugin" / "plugin.json").write_text(json.dumps(payloads["codex"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payloads
