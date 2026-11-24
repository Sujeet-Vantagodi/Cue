import { useState } from "react";
import { createEvent, executeEvent, getReceipts, undoAction, type EventResponse, type TrustMode } from "./api";

const examples = ["I got an internship in Hyderabad starting Jan 5", "I'm moving out of my PG next month", "I lost my phone"];

function plannerLabel(result: EventResponse): string {
  if (result.provider !== "local-template") return `${result.provider} planner · schema validated`;
  const reason = result.fallback_reason ?? "";
  if (reason.includes("429")) return "Gemini rate limit reached · local planner active";
  if (reason.includes("503")) return "Gemini temporarily unavailable · local planner active";
  if (reason.includes("ollama") && reason.includes("gemini")) return "Gemini and Ollama unavailable · local planner active";
  if (reason.includes("ollama")) return "Ollama unavailable · local planner active";
  if (reason.includes("gemini")) return "Gemini unavailable · local planner active";
  if (reason.includes("all LLM providers failed")) return "LLM providers unavailable · local planner active";
  return "Local planner active · schema validated";
}

export default function App() {
  const [text, setText] = useState("");
  const [mode, setMode] = useState<TrustMode>("ask");
  const [result, setResult] = useState<EventResponse>();
  const [selected, setSelected] = useState<string[]>([]);
  const [receipts, setReceipts] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function plan() { if (!text.trim()) return; setBusy(true); setMessage(""); try { const next = await createEvent(text, mode); setResult(next); setSelected(next.plan.tasks.flatMap(t => t.actions.filter(a => a.decision.allowed && !a.decision.needs_approval).map(a => a.id))); } catch (e) { setMessage(e instanceof Error ? e.message : "Something went wrong"); } finally { setBusy(false); } }
  async function approve() { if (!result) return; setBusy(true); try { const next = await executeEvent(result.plan.event_id, selected); setReceipts(next.receipts); setMessage("Approved actions completed. Rejected actions were not run."); } catch (e) { setMessage(e instanceof Error ? e.message : "Something went wrong"); } finally { setBusy(false); } }
  async function loadReceipts() { try { setReceipts((await getReceipts()).receipts); } catch { setMessage("Start the backend to view receipts."); } }
  async function undo(actionId: string) { try { await undoAction(actionId); setReceipts((await getReceipts()).receipts); setMessage("Action undone."); } catch (e) { setMessage(e instanceof Error ? e.message : "Could not undo action"); } }
  const allActions = result?.plan.tasks.flatMap(t => t.actions) ?? [];
  return <main>
    <header><div className="brand"><span className="mark">✦</span><span>Cue</span></div><div className="tagline">Life events, handled carefully.</div><button className="quiet" onClick={loadReceipts}>Receipts</button></header>
    <section className="hero"><p className="eyebrow">YOUR NEXT CHAPTER</p><h1>Tell me what happened.<br /><em>I’ll map what happens next.</em></h1><p className="lead">Cue turns one life event into a clear, sourced plan across your everyday tools—with your approval before anything changes.</p>
      <div className="composer"><textarea value={text} onChange={e => setText(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) plan(); }} placeholder="e.g. I got an internship in Hyderabad starting Jan 5" /><button onClick={plan} disabled={busy}>{busy ? "Thinking…" : "Make a plan  →"}</button></div>
      <div className="examples">Try <span>{examples.map(example => <button key={example} onClick={() => setText(example)}>{example}</button>)}</span></div>
    </section>
    <section className="trust"><div><strong>Trust dial</strong><span>Choose how much Cue can do</span></div><div className="dial">{(["observe", "ask", "assist"] as TrustMode[]).map(item => <button className={mode === item ? "active" : ""} onClick={() => setMode(item)} key={item}>{item[0].toUpperCase() + item.slice(1)}{item === "ask" && <small>recommended</small>}</button>)}</div></section>
    {message && <div className="notice">{message}</div>}
    {result && <section className="workspace"><div className="section-heading"><div><p className="eyebrow">BLAST RADIUS</p><h2>{result.plan.summary}</h2></div><span className="safe">✦ Nothing runs without your say-so</span></div><div className="source"><span>◉</span><div><strong>Evidence trail</strong><p>{result.evidence[0].snippet} <span className="source-chip">{result.evidence[0].source}</span></p></div></div><div className="brain">{plannerLabel(result)}</div>{result.plan.tasks.map(task => <div className="task" key={task.id}><h3>{task.title}</h3>{task.actions.map(action => <label className={`action ${selected.includes(action.id) ? "picked" : ""}`} key={action.id}><input type="checkbox" checked={selected.includes(action.id)} disabled={!action.decision.allowed} onChange={() => setSelected(current => current.includes(action.id) ? current.filter(id => id !== action.id) : [...current, action.id])} /><span className="app-icon">{action.app[0].toUpperCase()}</span><span className="action-copy"><strong>{action.tool.replaceAll("_", " ")}</strong><span>{JSON.stringify(action.args)}</span></span><span className={`tier ${action.tier.toLowerCase()}`}>{action.tier}{action.decision.needs_approval && " · approve"}</span></label>)}</div>)}<div className="action-bar"><span>{selected.length} action{selected.length === 1 ? "" : "s"} selected</span><button onClick={approve} disabled={busy || mode === "observe" || selected.length === 0}>{mode === "observe" ? "Observe mode is read-only" : "Approve selected  →"}</button></div></section>}
    {receipts.length > 0 && <section className="receipts"><div className="section-heading"><div><p className="eyebrow">AUDIT LEDGER</p><h2>Receipts</h2></div><span className="safe">Append-only record</span></div>{receipts.map(item => <div className="receipt" key={item.id}><span className="check">✓</span><span><strong>{item.tool.replaceAll("_", " ")}</strong><small>{item.status} · {item.created_at}{item.result_json?.includes("local-demo") && " · local demo adapter"}</small></span><span className="receipt-tier">{item.tier}</span>{item.status === "done" && <button className="undo" onClick={() => undo(item.id)}>Undo</button>}</div>)}</section>}
    <footer><span>◈ Cue</span><span>Reading is automatic. Writing needs approval.</span></footer>
  </main>;
}
