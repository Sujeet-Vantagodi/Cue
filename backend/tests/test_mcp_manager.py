from pathlib import Path

import pytest

from app.guardrails import Guardrails
from app.mcp_client.manager import MCPManager


@pytest.mark.asyncio
async def test_missing_adapter_is_explicit() -> None:
    manager = MCPManager(Guardrails(Path(__file__).parents[1] / "app" / "tools_registry.yaml"))
    result = await manager.call("calendar_create_event", {"title": "test"})
    assert result["status"] == "adapter_missing"

