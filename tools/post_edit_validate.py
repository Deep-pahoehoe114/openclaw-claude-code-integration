#!/usr/bin/env python3
"""Run post-edit validation for changed files."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def detect_changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="explicit changed files")
    args = parser.parse_args()

    changed = args.files or detect_changed_files()
    command = ["python3", "tools/run_checks.py"]
    if changed:
        command.extend(["--changed", *changed])
    else:
        command.append("--all")

    result = subprocess.run(command, check=False)
    if result.returncode == 0:
        print("post-edit validation passed")
        return 0

    print("post-edit validation failed")
    print("Suggested next steps:")
    print("- Inspect the failing command above")
    print("- Re-run `python3 tools/run_checks.py --all` after the fix")
    print("- If the failure is manifest drift, run `python3 tools/sync_repo_state.py`")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
