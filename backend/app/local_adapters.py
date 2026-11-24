from __future__ import annotations

import uuid
from typing import Any


class LocalDemoAdapters:
    """Deterministic local adapters used until real MCP sessions are connected."""

    def __init__(self) -> None:
        self.created: dict[str, dict[str, Any]] = {}

    async def create(self, args: dict[str, Any]) -> dict[str, Any]:
        external_id = f"cue_demo_{uuid.uuid4().hex[:10]}"
        item = {"external_id": external_id, "created_by": "cue", "args": args}
        self.created[external_id] = item
        return {"status": "done", "adapter": "local-demo", **item}

    async def undo(self, args: dict[str, Any]) -> dict[str, Any]:
        external_id = args.get("external_id")
        if external_id not in self.created:
            return {"status": "already_undone", "external_id": external_id}
        self.created.pop(external_id)
        return {"status": "undone", "adapter": "local-demo", "external_id": external_id}
