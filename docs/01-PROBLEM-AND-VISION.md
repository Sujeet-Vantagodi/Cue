# 01. Problem and Vision

**Read this first.** Summary: Cue is for regular people, not developers. It turns one sentence about a life event into a safe, approved, multi-app action plan.

## 1.1 Who we build for

A regular person who already uses Gmail, a calendar and a notes app: students starting a job, young professionals relocating, families preparing for a wedding or travel, anyone handling a stressful event. They are **not technical** and they **do not trust AI with real actions** by default.

## 1.2 The real problems

1. **Life events create scattered tasks.** A new job or a move spawns dozens of to-dos across email, calendar, notes and websites. No single place connects them.
2. **Details are buried in email.** Offer letters, deadlines, document requirements and confirmations sit in inboxes and get missed.
3. **People rebuild the same checklist every time.** "What documents do I need?" gets searched from scratch for each event.
4. **Apps do not talk to each other.** The user copies dates, retypes details and sets reminders by hand.
5. **Research is slow and fragmented.** Travel, rentals and document rules mean many tabs.
6. **AI assistants answer one question at a time.** They do not take a whole situation and carry it across apps.
7. **People do not trust AI with real actions.** Fear of wrong emails or deleted events blocks adoption.
8. **Mistakes cost real things:** missed deadlines, lost money, lost opportunities.

## 1.3 The vision

> Other AI waits for commands. Cue handles life events, and asks permission before it touches anything.

The hackathon brief says: *build an MCP-powered solution a regular person would use every day, with useful, reliable and controlled interactions.* Cue maps to that directly:

| Brief says | Cue's answer |
|---|---|
| Regular person, every day | Life-event sentences anyone can write |
| Go beyond basic integrations | Multi-step planning across 3 apps plus web research |
| Useful | Real checklists, calendar events, drafts, sourced research |
| Reliable | Dual-LLM failover, evidence trails, deterministic guardrails |
| Controlled | Trust Dial, Blast Radius, approvals, never-send, undo ledger |

## 1.4 Success criteria (what the judges must see)

1. A single sentence produces a complete, sourced plan.
2. The Blast Radius screen shows every change before it happens.
3. The user approves some actions and rejects others, and only approved ones run.
4. The audit log shows what happened, and undo works on at least one action.
5. Killing the primary LLM mid-demo does not break the flow (failover).

## 1.5 Non-goals (do not build these in 48 hours)

- WhatsApp, YouTube or LinkedIn integrations (no reliable MCP servers)
- Sending emails automatically
- Payments, logins or form submissions in the browser
- Multi-user accounts, billing, mobile apps
- Training or fine-tuning any model

## 1.6 Demo life events

- **Primary:** "I got an internship in Hyderabad starting Jan 5."
- **Secondary (shows generality):** "I'm moving out of my PG next month." or "I lost my phone."

Next: [`02-ARCHITECTURE.md`](02-ARCHITECTURE.md)
