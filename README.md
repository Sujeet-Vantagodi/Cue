# Cue

> **Tell it what happened. It plans the fallout. You approve every move.**

Cue is an MCP-powered life-event agent. You type **one sentence** about something that just happened to you ("I got an internship in Hyderabad starting Jan 5"). Cue figures out everything that now needs to happen, gathers the facts from your own Gmail and the web, and shows you a **Blast Radius preview** of exactly what it wants to change across Gmail, Google Calendar and Notion. Nothing is written until you approve it. Every action is logged and can be undone.

Built for the **"Make MCP Matter" hackathon**: *less magic, more utility.*

---

## 1. About Cue

**Problem statement:** *Make MCP Matter.* Build an MCP-powered solution a regular person would actually use every day, with useful, reliable and controlled interactions.

**Our answer:** Cue, an agent that moves from "AI that talks" to "AI that acts, safely." It handles the scattered tasks that follow a life event across the apps people already use.

---

## 2. The problem

Big life events (a new job, a move, a wedding, a lost phone) create **dozens of small tasks scattered across email, calendar, notes and websites**. The details are buried in inboxes, people rebuild the same checklist every time, and apps do not talk to each other, so the human becomes the glue. Existing AI assistants answer one question at a time, and people do not trust AI to take real actions without supervision.

Full breakdown: [`docs/01-PROBLEM-AND-VISION.md`](docs/01-PROBLEM-AND-VISION.md)

---

## 3. What makes Cue different

| Signature feature | What it means |
|---|---|
| **One-sentence life events** | You describe what happened, not what to do. Cue builds the whole task graph. |
| **Blast Radius preview** | Before anything changes, Cue shows every app, every item and every field it will touch, in one screen. |
| **Trust Dial** | The user picks: **Observe** (read only), **Ask** (approve each action), or **Assist** (auto-run only low-risk actions). Default is Ask. |
| **Receipts and Undo ledger** | Every write is logged with before/after state and an undo handler. |
| **Evidence trails** | Every extracted fact links to its source (the exact email or web page). No unsourced claims. |
| **Never-send rule** | Cue can only create email **drafts**. Sending is not exposed to the model at all. |
| **Read-only browser sandbox** | Playwright can open and read allow-listed pages, but cannot click, type, log in or submit. |
| **Dual-brain failover** | Two switchable LLMs behind one interface. If the primary fails or rate-limits, Cue falls back automatically. |

---

## 4. Reading order (start here)

Read these in order. Each file is self-contained, and each builds on the previous one. If you are an AI coding agent, **read all of them before writing code**, then follow `docs/08-AI-BUILD-GUIDE.md`.

| # | File | One-line summary |
|---|---|---|
| 1 | [`docs/01-PROBLEM-AND-VISION.md`](docs/01-PROBLEM-AND-VISION.md) | Who we build for, the pain points, and what "success" looks like. |
| 2 | [`docs/02-ARCHITECTURE.md`](docs/02-ARCHITECTURE.md) | System design: planner, guardrails, approval, MCP client, ledger. |
| 3 | [`docs/03-TECH-STACK.md`](docs/03-TECH-STACK.md) | Every tool and library, why it was chosen, and the free-tier plan. |
| 4 | [`docs/04-GUARDRAILS-AND-SAFETY.md`](docs/04-GUARDRAILS-AND-SAFETY.md) | Risk tiers, Trust Dial, allowlists, never-send rule, undo. |
| 5 | [`docs/05-PLAN-SCHEMA-AND-TOOLS.md`](docs/05-PLAN-SCHEMA-AND-TOOLS.md) | The exact JSON plan format, tool registry and prompts. |
| 6 | [`docs/06-BUILD-TIMELINE-48H.md`](docs/06-BUILD-TIMELINE-48H.md) | Hour-by-hour plan for the 48-hour hackathon. |
| 7 | [`docs/07-DEMO-SCRIPT.md`](docs/07-DEMO-SCRIPT.md) | The 90-second demo, the pitch, and answers to judge questions. |
| 8 | [`docs/08-AI-BUILD-GUIDE.md`](docs/08-AI-BUILD-GUIDE.md) | Instructions for an AI coding agent: repo layout, build order, acceptance tests. |

---

## 5. How it works (30-second version)

```
"I got an internship in Hyderabad starting Jan 5"
        |
        v
  [1] Understand  -> life event type + key facts + missing info
  [2] Plan        -> task graph as structured JSON
  [3] Gather      -> READ-ONLY: Gmail search, web search, browser reads
  [4] Propose     -> Blast Radius preview (every change, with evidence)
  [5] Approve     -> user approves / edits / rejects each action
  [6] Execute     -> only approved actions run via MCP tools
  [7] Receipt     -> ledger entry + one-tap undo
```

Details: [`docs/02-ARCHITECTURE.md`](docs/02-ARCHITECTURE.md)

---

## 6. Integrations (all free-tier)

- **Gmail** (MCP): search, read, **create draft only**
- **Google Calendar** (MCP): create events and reminders, with approval
- **Notion** (MCP): create checklist and tracker pages, with approval
- **Web search** (MCP): DuckDuckGo keyless, with Tavily/Exa as fallback
- **Playwright** (MCP): read-only browsing of allow-listed pages
- **LLMs**: primary (Gemini API free tier) plus fallback (second provider or local model), behind one `call_llm()` interface

Free-tier limits change. Verify each quota before the event. See [`docs/03-TECH-STACK.md`](docs/03-TECH-STACK.md).

---

## 7. Quick start

```bash
git clone <your-repo-url> cue && cd cue
cp .env.example .env        # add keys (see docs/03-TECH-STACK.md)
# backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# frontend (new terminal)
cd frontend && npm install && npm run dev
```

Open the web app, connect Google and Notion, type a life event, and review the Blast Radius.

---

## 8. Design principles

1. **Reading is automatic. Writing needs approval.**
2. **If unsure, ask.** Ambiguity produces a question, not a guess.
3. **Everything is sourced.** No fact without evidence.
4. **Everything is reversible** where the underlying app allows it.
5. **The model proposes. The guardrail layer decides.** The LLM never calls a write tool directly.

---

## 9. License

MIT (add a `LICENSE` file before submission).
