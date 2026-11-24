# 02. Architecture

Summary: a pipeline where the **LLM proposes** and a **deterministic guardrail layer decides**. The LLM never calls write tools directly.

## 2.1 High-level diagram

```
                    +---------------------+
   User sentence -->|  Web UI (chat +     |
                    |  Blast Radius view) |
                    +----------+----------+
                               | HTTP / WebSocket
                    +----------v----------+
                    |   FastAPI backend   |
                    +----------+----------+
                               |
     +-------------+-----------+-----------+--------------+
     |             |                       |              |
+----v-----+  +----v------+        +-------v------+  +----v-----+
| Planner  |  | Guardrail |        |  Executor    |  | Ledger   |
| (LLM)    |  | engine    |        | (MCP client) |  | (SQLite) |
+----+-----+  +----+------+        +-------+------+  +----+-----+
     |             |                       |              |
+----v-----+       |        +--------------+---------+    |
| LLM      |       |        | MCP servers            |    |
| Router   |       |        | Gmail | Calendar |     |    |
| primary/ |       |        | Notion | Search |      |    |
| fallback |       |        | Playwright (read-only) |    |
+----------+       |        +------------------------+    |
                   +-- decides READ / WRITE / RISKY / BLOCKED
```

## 2.2 Components

| Component | Responsibility | Key rule |
|---|---|---|
| **Web UI** | Input box, plan view, Blast Radius, approve/reject buttons, audit log, Trust Dial | Never calls MCP servers itself |
| **Planner** | Turns the sentence plus gathered evidence into a structured plan (JSON) | Output must validate against the schema in doc 05 |
| **LLM Router** | One `call_llm()` function, primary and fallback providers, retries, timeouts | Swappable in under a minute |
| **Guardrail engine** | Tags every proposed action with a risk tier and decides if it may run | Pure code, no LLM involved |
| **Executor / MCP client** | Calls MCP tools for approved actions only | Refuses any tool not in the registry |
| **Ledger** | Stores each action, its inputs, result, before/after state and undo handler | Append-only |
| **Evidence store** | Maps each fact to its source (email id, URL, snippet) | Every plan item carries evidence ids |

## 2.3 The 7-step flow

1. **Understand.** LLM classifies the event type (`new_job_relocation`, `moving_out`, `lost_phone`, `other`), extracts facts (city, date, company), and lists missing info. If critical info is missing, ask the user one short question.
2. **Plan.** LLM drafts a task graph: tasks, dependencies, and the tool each task would use.
3. **Gather (READ only).** The executor runs read-tier tools automatically: Gmail search, web search, page reads. Results go into the evidence store.
4. **Propose.** LLM revises the plan using evidence and emits concrete actions (events, checklist items, drafts). The guardrail engine tags each one.
5. **Blast Radius.** UI shows every action grouped by app, with evidence links, risk tier, and approve/edit/reject controls.
6. **Execute.** Only approved actions run through the MCP client. Order follows task dependencies.
7. **Receipt.** Each result is written to the ledger. The UI offers one-tap undo where supported.

## 2.4 Blast Radius preview

For every proposed action show: **app, operation, target item, exact fields to be written, evidence source, risk tier, and undo availability.** Example row:

```
Google Calendar | create_event | "Join Acme Corp, Hyderabad" | 2027-01-05 09:30 IST
Evidence: offer_letter.pdf in email "Offer of Employment" (msg_8f2a) | Tier: WRITE | Undo: yes
```

## 2.5 LLM Router behavior

```
call_llm(messages, schema=None):
    try primary (timeout 20s, 1 retry)
    on rate limit / error / timeout / invalid JSON after 1 repair attempt:
        try fallback
    log which provider answered
    return parsed result
```

Provider choices and free-tier notes are in doc 03.

## 2.6 Data stores

SQLite, three tables: `events` (life events and status), `actions` (proposed and executed actions with tier, status and undo payload), `evidence` (source references). No external database.

## 2.7 Failure handling

| Failure | Behavior |
|---|---|
| Primary LLM fails | Fallback LLM answers, UI shows a small "backup brain" badge |
| Invalid JSON from LLM | One repair attempt, then ask user or abort the step |
| MCP tool error | Mark the action failed, continue independent actions, show the error |
| Ambiguous evidence (two offer letters) | Ask the user to choose |
| Search rate limit | Fall through the search provider chain |

Next: [`03-TECH-STACK.md`](03-TECH-STACK.md)
