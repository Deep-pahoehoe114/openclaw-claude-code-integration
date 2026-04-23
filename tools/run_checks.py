#!/usr/bin/env python3
"""Run markdown-defined checks from .openclaw/checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oeck.runtime_core.validation import load_checks, run_check, select_checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="run all checks")
    parser.add_argument("--changed", nargs="*", default=[], help="changed files for trigger matching")
    args = parser.parse_args()

    root = Path.cwd()
    checks_dir = root / ".openclaw" / "checks"
    checks = load_checks(checks_dir)
    selected = checks if args.all else select_checks(checks, args.changed)
    if not selected:
        print("no checks selected")
        return 0

    failures = []
    for check in selected:
        print(f"[check] {check.name}: {check.description}")
        results = run_check(check, root)
        for command, code in results:
            print(f"  - `{command}` -> {code}")
            if code != 0:
                failures.append((check.name, command, code))
                break

    if failures:
        print("\n[failed]")
        for name, command, code in failures:
            print(f"- {name}: `{command}` exited with {code}")
        return 1

    print("\n[ok] all selected checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
