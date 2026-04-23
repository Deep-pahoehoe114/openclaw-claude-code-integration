# Manual

This repository is now centered on the OECK runtime and generated distribution assets.

## Daily Commands

- Sync manifests and generated docs:
  `python3 tools/sync_repo_state.py`
- Run all checks:
  `python3 tools/run_checks.py --all`
- Run post-edit validation:
  `python3 tools/post_edit_validate.py`
- Print repo summary:
  `python3 tools/repo_map.py --summary`

## Runtime Layout

- `metadata/canonical.json`: single source of truth
- `oeck/runtime_core/`: policy, context, session, memory, sandbox, tracing
- `oeck/adapters/`: distribution and optional adapters
- `.openclaw/checks/`: shared checks
- `skills/`: content assets and compatibility shims

## Optional Integrations

- Observability: JSONL by default, Opik placeholder adapter included
- Temporal memory: local stub only by default
- Remote sandbox: interface + no-op adapter only by default
- Lossless context: file-backed adapter available, disabled by default
