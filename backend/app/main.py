from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .guardrails import GuardrailError, Guardrails
from .executor import Executor
from .ledger import Ledger
from .local_adapters import LocalDemoAdapters
from .google_calendar import GoogleCalendarAdapter
from .mcp_client.manager import MCPManager
from .models import Action, ApprovalRequest, CreateEventRequest, Evidence, TrustMode
from .planner import generate_plan

ROOT = Path(__file__).parent
PROJECT_ROOT = ROOT.parent.parent
load_dotenv(PROJECT_ROOT / ".env")
ledger = Ledger(os.getenv("DATABASE_PATH", "./cue.db"))
guardrails = Guardrails(ROOT / "tools_registry.yaml", os.getenv("BROWSER_ALLOWLIST", "").split(","))
manager = MCPManager(guardrails)
executor = Executor(manager, ledger)
local_adapters = LocalDemoAdapters()
for tool in ("gmail_create_draft", "calendar_create_event", "notion_create_page"):
    manager.register(tool, local_adapters.create)
for tool in ("gmail_delete_draft", "calendar_delete_event", "notion_archive_page"):
    manager.register(tool, local_adapters.undo)
if (ROOT.parent / "credentials.json").exists():
    google_calendar = GoogleCalendarAdapter(ROOT.parent / "credentials.json", ROOT.parent / "token.json")
    manager.register("calendar_create_event", google_calendar.create)
    manager.register("calendar_delete_event", google_calendar.undo)
app = FastAPI(title="Cue", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


def public_plan(plan, mode: TrustMode) -> dict:
    data = plan.model_dump(mode="json")
    evidence = [Evidence(id="ev_user", source="user_input", title="Your event", snippet="Facts extracted from your sentence.", trusted=True).model_dump()]
    for task in plan.tasks:
        for action in task.actions:
            try:
                normalized = guardrails.normalize(Action.model_validate(action))
            except GuardrailError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            decision = guardrails.decide(normalized, mode)
            action_data = normalized.model_dump(mode="json")
            action_data["decision"] = decision.__dict__
            action_data["evidence_ids"] = action_data.get("evidence_ids") or ["ev_user"]
            task_data = next(item for item in data["tasks"] if item["id"] == task.id)
            next(item for item in task_data["actions"] if item["id"] == action.id).update(action_data)
    return {"plan": data, "evidence": evidence}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "cue"}


@app.get("/api/status")
def status() -> dict[str, str | bool]:
    return {
        "service": "cue",
        "llm_primary": os.getenv("LLM_PRIMARY", "mock"),
        "llm_fallback": os.getenv("LLM_FALLBACK", "mock"),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "mode": "local-demo",
    }


@app.post("/api/events")
def create_event(request: CreateEventRequest) -> dict:
    plan, provider, fallback_reason = generate_plan(request.text)
    result = public_plan(plan, request.trust_mode)
    result["provider"] = provider
    result["fallback_reason"] = fallback_reason
    ledger.save_event(plan.event_id, request.text, request.trust_mode.value, result["plan"])
    return result


@app.post("/api/events/{event_id}/execute")
async def execute_event(event_id: str, request: ApprovalRequest) -> dict:
    event = ledger.db.execute("SELECT plan, trust_mode FROM events WHERE id=?", (event_id,)).fetchone()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    plan = __import__("json").loads(event["plan"])
    mode = TrustMode(event["trust_mode"])
    actions: list[Action] = []
    approved_ids: set[str] = set()
    requested = set(request.approved_action_ids)
    for raw in (raw_action for task in plan["tasks"] for raw_action in task["actions"]):
        action = guardrails.normalize(Action.model_validate(raw))
        decision = guardrails.decide(action, mode)
        if action.id in requested and decision.allowed and (not decision.needs_approval or action.id in requested):
            approved_ids.add(action.id)
        actions.append(action)
    executed = await executor.execute(event_id, actions, approved_ids)
    return {"event_id": event_id, "executed": executed, "receipts": ledger.list_actions(event_id)}


@app.get("/api/receipts")
def receipts() -> dict:
    return {"receipts": ledger.receipts()}


@app.post("/api/actions/{action_id}/undo")
async def undo_action(action_id: str) -> dict:
    row = ledger.action(action_id)
    if not row:
        raise HTTPException(status_code=404, detail="Action not found")
    if row["status"] not in {"done", "waiting_for_adapter"}:
        raise HTTPException(status_code=409, detail="Only completed actions can be undone")
    result = __import__("json").loads(row["result_json"] or "{}")
    external_id = result.get("external_id")
    undo_tool = guardrails.registry.get(row["tool"], {}).get("undo")
    if not undo_tool or not external_id:
        raise HTTPException(status_code=409, detail="This action has no supported undo handler")
    undo_result = await manager.call(undo_tool, {"external_id": external_id})
    ledger.save_action(row["event_id"], action_id, row["tool"], row["tier"], "undone", __import__("json").loads(row["input_json"]), undo_result)
    return {"action_id": action_id, "status": "undone", "result": undo_result}
