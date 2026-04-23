# Quickstart

## Generate Distribution Assets

```bash
python3 tools/sync_repo_state.py
```

## Run Validation

```bash
python3 tools/run_checks.py --all
python3 tools/post_edit_validate.py
```

## Inspect The Codebase

```bash
python3 tools/repo_map.py --summary
python3 tools/smoke_test.py
```

## Pick A Host Target

1. OpenClaw native plugin: `openclaw.plugin.json`
2. Claude bundle: `.claude-plugin/plugin.json`
3. Codex bundle: `.codex-plugin/plugin.json`

Development installs should link or install the relevant manifest/bundle. Legacy `cp -r skills/*` remains a compatibility fallback, not the default.
