from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from ..guardrails import GuardrailError, Guardrails

ToolHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class MCPManager:
    """Small logical-tool gateway.

    Real MCP sessions can be registered here later. The rest of Cue only sees
    logical names from tools_registry.yaml, so provider-specific names never
    leak into the planner or frontend.
    """

    def __init__(self, guardrails: Guardrails) -> None:
        self.guardrails = guardrails
        self.handlers: dict[str, ToolHandler] = {}

    def register(self, logical_name: str, handler: ToolHandler) -> None:
        if logical_name not in self.guardrails.registry:
            raise GuardrailError(f"Cannot register unknown tool '{logical_name}'")
        self.handlers[logical_name] = handler

    async def call(self, logical_name: str, args: dict[str, Any]) -> dict[str, Any]:
        if logical_name not in self.guardrails.registry:
            raise GuardrailError(f"Tool '{logical_name}' is not registered")
        handler = self.handlers.get(logical_name)
        if handler is None:
            return {"status": "adapter_missing", "tool": logical_name, "message": "Connect the corresponding MCP server to execute this tool."}
        return await handler(args)
