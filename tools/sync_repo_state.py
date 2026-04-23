#!/usr/bin/env python3
"""Generate manifests, generated docs, and keep markdown sections in sync."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oeck.distribution import build_distribution_assets, render_generated_docs
from oeck.runtime_core.workspace import WorkspaceResolver


def replace_marked_section(content: str, marker: str, replacement: str) -> str:
    start = f"<!-- {marker}:start -->"
    end = f"<!-- {marker}:end -->"
    if start not in content or end not in content:
        raise ValueError(f"missing marker {marker}")
    before, remainder = content.split(start, 1)
    _, after = remainder.split(end, 1)
    return f"{before}{start}\n{replacement.rstrip()}\n{end}{after}"


def sync_markdown_file(path: Path, generated: dict) -> None:
    content = path.read_text(encoding="utf-8")
    content = replace_marked_section(content, "generated-skills", generated["skills_section"])
    content = replace_marked_section(content, "generated-tests", generated["tests_section"])
    content = replace_marked_section(content, "generated-tree", generated["tree_section"])
    content = replace_marked_section(content, "generated-adapters", generated["adapters_section"])
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated content without rewriting")
    args = parser.parse_args()

    resolver = WorkspaceResolver.from_workspace(Path.cwd())
    generated = render_generated_docs(resolver)
    build_distribution_assets(resolver)

    readmes = [
        resolver.layout.workspace_root / "README.md",
        resolver.layout.workspace_root / "README_CN.md",
        resolver.layout.workspace_root / "INTEGRATION_SUMMARY.md",
    ]

    if args.check:
        for path in readmes:
            original = path.read_text(encoding="utf-8")
            updated = original
            updated = replace_marked_section(updated, "generated-skills", generated["skills_section"])
            updated = replace_marked_section(updated, "generated-tests", generated["tests_section"])
            updated = replace_marked_section(updated, "generated-tree", generated["tree_section"])
            updated = replace_marked_section(updated, "generated-adapters", generated["adapters_section"])
            if original != updated:
                print(f"out of date: {path}")
                return 1
        return 0

    for path in readmes:
        sync_markdown_file(path, generated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
