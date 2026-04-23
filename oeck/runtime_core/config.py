"""Configuration loading for OECK."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


def _find_workspace_root(explicit: str | Path | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    candidates = [
        Path(os.environ["OECK_WORKSPACE"]).expanduser() if os.environ.get("OECK_WORKSPACE") else None,
        Path(os.environ["OPENCLAW_WORKSPACE"]).expanduser() if os.environ.get("OPENCLAW_WORKSPACE") else None,
        Path.cwd(),
    ]
    for candidate in candidates:
        if candidate and (candidate / "metadata" / "canonical.json").exists():
            return candidate.resolve()
    for base in [Path.cwd(), *Path.cwd().parents]:
        if (base / "metadata" / "canonical.json").exists():
            return base.resolve()
    return Path.cwd().resolve()


def _read_json_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class KitConfig:
    workspace_root: Path
    host_home: Path
    state_dir: Path
    session_dir: Path | None
    memory_backend: str = "auto"
    trace_backend: str = "jsonl"
    sandbox_backend: str = "local"
    mode: str = "build"
    approval_profile: str = "default"
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    adapter_flags: Dict[str, bool] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)


def load_kit_config(workspace_hint: str | Path | None = None) -> KitConfig:
    workspace_root = _find_workspace_root(workspace_hint)
    config_path = workspace_root / "oeck.config.json"
    file_config = _read_json_config(config_path)

    host_home = Path(
        os.environ.get(
            "OPENCLAW_HOME",
            file_config.get("host_home", str(Path.home() / ".openclaw")),
        )
    ).expanduser()
    state_dir = Path(
        os.environ.get(
            "OECK_STATE_DIR",
            file_config.get("state_dir", str(workspace_root / ".oeck")),
        )
    ).expanduser()

    session_value = os.environ.get("OECK_SESSION_DIR") or file_config.get("session_dir")
    session_dir = Path(session_value).expanduser() if session_value else None

    feature_flags = {
        "lossless_context": bool(file_config.get("feature_flags", {}).get("lossless_context", False)),
        "observability": bool(file_config.get("feature_flags", {}).get("observability", True)),
        "temporal_memory": bool(file_config.get("feature_flags", {}).get("temporal_memory", False)),
        "remote_sandbox": bool(file_config.get("feature_flags", {}).get("remote_sandbox", False)),
    }
    feature_flags.update(
        {
            key.removeprefix("OECK_FEATURE_").lower(): value.lower() in {"1", "true", "yes", "on"}
            for key, value in os.environ.items()
            if key.startswith("OECK_FEATURE_")
        }
    )

    adapter_flags = {
        "claude_bundle": True,
        "codex_bundle": True,
        "openclaw_native": True,
    }
    adapter_flags.update(file_config.get("adapter_flags", {}))

    return KitConfig(
        workspace_root=workspace_root,
        host_home=host_home,
        state_dir=state_dir,
        session_dir=session_dir,
        memory_backend=os.environ.get("OECK_MEMORY_BACKEND", file_config.get("memory_backend", "auto")),
        trace_backend=os.environ.get("OECK_TRACE_BACKEND", file_config.get("trace_backend", "jsonl")),
        sandbox_backend=os.environ.get("OECK_SANDBOX_BACKEND", file_config.get("sandbox_backend", "local")),
        mode=os.environ.get("OECK_MODE", file_config.get("mode", "build")),
        approval_profile=os.environ.get("OECK_APPROVAL_PROFILE", file_config.get("approval_profile", "default")),
        feature_flags=feature_flags,
        adapter_flags=adapter_flags,
        extra=file_config.get("extra", {}),
    )
