export type TrustMode = "observe" | "ask" | "assist";
export type Action = { id: string; app: string; tool: string; args: Record<string, unknown>; tier: string; low_risk: boolean; evidence_ids: string[]; decision: { allowed: boolean; needs_approval: boolean; reason: string } };
export type Plan = { event_id: string; summary: string; tasks: { id: string; title: string; actions: Action[] }[] };
export type EventResponse = { plan: Plan; evidence: { id: string; title: string; snippet: string; source: string }[]; provider: string; fallback_reason?: string | null };

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export async function createEvent(text: string, trust_mode: TrustMode): Promise<EventResponse> {
  const response = await fetch(`${API}/api/events`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, trust_mode }) });
  if (!response.ok) throw new Error((await response.json()).detail ?? "Could not create event");
  return response.json();
}
export async function executeEvent(eventId: string, approved_action_ids: string[]) {
  const response = await fetch(`${API}/api/events/${eventId}/execute`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ approved_action_ids }) });
  if (!response.ok) throw new Error("Could not execute event");
  return response.json();
}
export async function getReceipts() { return (await fetch(`${API}/api/receipts`)).json(); }
export async function undoAction(actionId: string) { const response = await fetch(`${API}/api/actions/${actionId}/undo`, { method: "POST" }); if (!response.ok) throw new Error((await response.json()).detail ?? "Could not undo action"); return response.json(); }
