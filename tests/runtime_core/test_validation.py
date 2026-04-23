from pathlib import Path

from oeck.runtime_core.validation import load_checks, select_checks


def test_load_checks_from_markdown_frontmatter():
    checks = load_checks(Path(".openclaw/checks"))

    assert any(check.name == "python-quality" for check in checks)
    assert any(check.commands for check in checks)


def test_select_checks_by_changed_file():
    checks = load_checks(Path(".openclaw/checks"))
    selected = select_checks(checks, ["metadata/canonical.json"])

    assert any(check.name == "distribution-consistency" for check in selected)
