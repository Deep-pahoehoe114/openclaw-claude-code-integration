"""Common adapter types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AdapterSpec:
    adapter_id: str
    summary: str
    enabled: bool
    optional: bool = True
