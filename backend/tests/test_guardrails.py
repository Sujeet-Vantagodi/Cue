from pathlib import Path

import pytest

from app.guardrails import GuardrailError, Guardrails
from app.models import Action, Tier, TrustMode


ROOT = Path(__file__).parents[1] / "app"


def test_registry_overwrites_llm_tier_and_sets_undo() -> None:
    policy = Guardrails(ROOT / "tools_registry.yaml")
    action = policy.normalize(Action(id="x", app="gmail", tool="gmail_create_draft", tier=Tier.READ))
    assert action.tier == Tier.WRITE
    assert action.undo and action.undo.tool == "gmail_delete_draft"


def test_unknown_tools_are_rejected() -> None:
    policy = Guardrails(ROOT / "tools_registry.yaml")
    with pytest.raises(GuardrailError):
        policy.normalize(Action(id="x", app="gmail", tool="gmail_send"))


def test_observe_mode_blocks_writes() -> None:
    policy = Guardrails(ROOT / "tools_registry.yaml")
    action = policy.normalize(Action(id="x", app="notion", tool="notion_create_page", low_risk=True))
    decision = policy.decide(action, TrustMode.OBSERVE)
    assert not decision.allowed

