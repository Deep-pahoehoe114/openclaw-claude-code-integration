+++
name = "python-quality"
description = "Compile and test Python runtime changes."
triggers = ["*.py", "oeck/*", "skills/*", "tests/*", "tools/*"]
commands = [
  "python3 -m compileall oeck skills tests tools",
  "pytest -q"
]
+++

# Python Quality

Runs compilation and pytest for Python-facing changes.
