from __future__ import annotations

from typing import Any

from .ledger import Ledger
from .mcp_client.manager import MCPManager
from .models import Action


class Executor:
    def __init__(self, manager: MCPManager, ledger: Ledger) -> None:
        self.manager, self.ledger = manager, ledger

    async def execute(self, event_id: str, actions: list[Action], approved_ids: set[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for action in actions:
            if action.id not in approved_ids:
                self.ledger.save_action(event_id, action.id, action.tool, action.tier.value, "rejected", action.args)
                continue
            self.ledger.save_action(event_id, action.id, action.tool, action.tier.value, "pending", action.args)
            try:
                result = await self.manager.call(action.tool, action.args)
                status = "done" if result.get("status") != "adapter_missing" else "waiting_for_adapter"
                self.ledger.save_action(event_id, action.id, action.tool, action.tier.value, status, action.args, result)
                results.append({"action_id": action.id, "status": status, "result": result})
            except Exception as exc:
                result = {"error": str(exc)}
                self.ledger.save_action(event_id, action.id, action.tool, action.tier.value, "failed", action.args, result)
                results.append({"action_id": action.id, "status": "failed", "result": result})
        return results
