"""Sandbox provider abstractions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .config import KitConfig


@dataclass(slots=True)
class SandboxDecision:
    allowed: bool
    provider: str
    reason: str
    details: dict = field(default_factory=dict)


class SandboxProvider(Protocol):
    def evaluate(self, command: str, mode: str) -> SandboxDecision:
        ...


class LocalSandboxProvider:
    def evaluate(self, command: str, mode: str) -> SandboxDecision:
        if mode == "review":
            return SandboxDecision(False, "local", "review mode is read-only")
        return SandboxDecision(True, "local", "local execution permitted by current mode")


class RemoteSandboxProviderStub:
    def evaluate(self, command: str, mode: str) -> SandboxDecision:
        return SandboxDecision(False, "remote-sandbox-stub", "remote sandbox adapter is disabled")


def create_sandbox_provider(config: KitConfig | None = None) -> SandboxProvider:
    backend = getattr(config, "sandbox_backend", "local")
    if backend == "remote":
        return RemoteSandboxProviderStub()
    return LocalSandboxProvider()
