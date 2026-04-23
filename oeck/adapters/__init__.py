"""Adapter interfaces and default implementations."""

from .base import AdapterSpec
from .distribution import ClaudeBundleAdapter, CodexBundleAdapter, OpenClawNativeAdapter
from .lossless_context import FileLosslessContextAdapter, NoOpLosslessContextAdapter
from .observability import JsonlObservabilityAdapter, NoOpObservabilityAdapter, OpikObservabilityAdapter
from .remote_sandbox import NoOpRemoteSandboxAdapter
from .temporal_memory import LocalTemporalMemoryAdapter, NoOpTemporalMemoryAdapter

__all__ = [
    "AdapterSpec",
    "ClaudeBundleAdapter",
    "CodexBundleAdapter",
    "FileLosslessContextAdapter",
    "JsonlObservabilityAdapter",
    "LocalTemporalMemoryAdapter",
    "NoOpLosslessContextAdapter",
    "NoOpObservabilityAdapter",
    "NoOpRemoteSandboxAdapter",
    "NoOpTemporalMemoryAdapter",
    "OpenClawNativeAdapter",
    "OpikObservabilityAdapter",
]
