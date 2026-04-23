"""Remote sandbox adapter placeholder."""

from __future__ import annotations


class NoOpRemoteSandboxAdapter:
    def provision(self) -> dict:
        return {
            "provisioned": False,
            "reason": "remote sandbox adapter is optional and currently disabled",
        }
