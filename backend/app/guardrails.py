from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml

from .models import Action, Tier, TrustMode


@dataclass(frozen=True)
class Decision:
    allowed: bool
    needs_approval: bool
    reason: str


class GuardrailError(ValueError):
    pass


class Guardrails:
    def __init__(self, registry_path: str | Path, allowlist: list[str] | None = None) -> None:
        self.registry = yaml.safe_load(Path(registry_path).read_text()) or {}
        self.allowlist = allowlist or []

    def normalize(self, action: Action) -> Action:
        spec = self.registry.get(action.tool)
        if not spec:
            raise GuardrailError(f"Tool '{action.tool}' is not registered")
        values = action.model_dump()
        values["tier"] = spec["tier"]
        values["app"] = spec["app"]
        values["low_risk"] = bool(action.low_risk and spec.get("low_risk_eligible", False))
        if spec.get("undo"):
            values["undo"] = {"tool": spec["undo"]}
        return Action.model_validate(values)

    def decide(self, action: Action, mode: TrustMode) -> Decision:
        if action.tier == Tier.BLOCKED:
            return Decision(False, False, "blocked tool")
        if mode == TrustMode.OBSERVE and action.tier != Tier.READ:
            return Decision(False, False, "Observe mode is read-only")
        if action.tier == Tier.READ:
            return Decision(True, False, "read-only action")
        if mode == TrustMode.ASSIST and action.tier == Tier.WRITE and action.low_risk:
            return Decision(True, False, "low-risk write in Assist mode")
        return Decision(True, True, "approval required")

    def check_url(self, url: str) -> None:
        host = urlparse(url).hostname or ""
        if not any(host == item or (item.startswith("*.") and host.endswith(item[1:])) for item in self.allowlist):
            raise GuardrailError(f"Domain '{host}' is not allow-listed")
