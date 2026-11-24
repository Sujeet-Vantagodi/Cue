# 08. AI Build Guide

**Audience: an AI coding agent (or a teammate) building Cue.** Read docs 01 to 07 first. This file tells you what to build, in what order, and how to know it works.

## 8.1 Mission

Build **Cue**: a web app where a user types one sentence about a life event, and the system plans, researches (read-only), shows a Blast Radius preview, executes only approved actions via MCP tools (Gmail drafts, Google Calendar events, Notion pages), logs everything, and supports undo.

## 8.2 Non-negotiable rules

1. The LLM never calls write tools directly. Flow is always: LLM proposes JSON, guardrail engine validates and tags, user approves, executor runs.
2. Do **not** register or implement send-email, delete-email, browser click/type/fill/submit, or any payment tool.
3. Tool tiers come from `tools_registry.yaml`, **not** from LLM output.
4. Treat email and web content as untrusted data.
5. All plan JSON is validated with Pydantic against doc 05. No exceptions.
6. Secrets only in `.env`. Never commit keys.
7. Keep it runnable locally with free tiers.

## 8.3 Repository layout

```
cue/
  README.md
  .env.example
  docs/                      # docs 01..08
  backend/
    requirements.txt
    app/
      main.py                # FastAPI app, routes, WebSocket
      config.py              # env loading
      models.py              # Pydantic models: Plan, Task, Action, Evidence
      planner.py             # extraction + plan generation + repair
      llm/
        router.py            # call_llm(), failover logic
        gemini.py            # primary provider
        fallback.py          # second provider (hosted or Ollama)
      mcp_client/
        manager.py           # connect to MCP servers, list tools, call tools
      guardrails/
        policy.py            # tier assignment, trust dial, allowlists, limits
        injection.py         # untrusted content wrapping and flagging
      tools_registry.yaml
      executor.py            # topological execution, READ auto, WRITE after approval
      ledger.py              # SQLite: events, actions, evidence, undo
      search_chain.py        # DDG -> Tavily -> Exa with cache
    tests/
      test_guardrails.py
      test_schema.py
      test_router.py
  frontend/
    src/
      App.tsx
      components/
        EventInput.tsx
        PlanView.tsx
        BlastRadius.tsx      # grouped by app, evidence links, approve/edit/reject
        TrustDial.tsx
        AuditLog.tsx         # receipts + undo
        BackupBrainBadge.tsx
      api.ts
```

## 8.4 Build order (follow strictly)

| Step | Build | Acceptance test |
|---|---|---|
| 1 | Config, FastAPI skeleton, SQLite ledger tables | `GET /health` returns ok; tables exist |
| 2 | `models.py` with schemas from doc 05 | Sample plan JSON validates; bad JSON fails with clear errors |
| 3 | `llm/router.py` with primary and fallback | Forcing primary to error returns a fallback response and logs provider |
| 4 | `mcp_client/manager.py`: connect each server, list tools | Script prints real tool names per server |
| 5 | `tools_registry.yaml` mapping logical names to real MCP tool names | Unknown tool call is rejected |
| 6 | `guardrails/policy.py` | Unit tests: tier overwrite works; blocked tools refused; Observe mode blocks writes; allowlist enforced |
| 7 | `search_chain.py` with cache | Search returns results; killing provider 1 falls to provider 2; repeat query hits cache |
| 8 | `planner.py`: extraction, plan, repair | Test sentence yields a validated plan; missing facts produce questions |
| 9 | READ pipeline: run READ actions, store evidence | Gmail search and web search results appear as evidence ids |
| 10 | Blast Radius API plus UI | UI lists every action by app with evidence, tier and undo availability |
| 11 | Approval endpoint plus executor (dependency order) | Only approved actions run; rejected ones never execute |
| 12 | Ledger entries plus undo handlers | Undo deletes the created event, Notion page or draft |
| 13 | Trust Dial setting wired through policy | Observe, Ask and Assist behave as in doc 04 |
| 14 | Playwright read-only tools with domain allowlist | Allowed domain readable; non-allowlisted domain refused; click/type tools do not exist |
| 15 | Injection test and blocked-tool log display | Injection email does not cause any proposed action; attempts show in log |
| 16 | Second event template, polish, error states | Both demo events pass end to end |

## 8.5 Definition of done (MVP)

- [ ] One sentence produces a validated, evidence-linked plan from real Gmail and web data
- [ ] Blast Radius screen shows all proposed writes before anything happens
- [ ] Approved actions create real Calendar events, Notion pages and Gmail drafts
- [ ] Rejected actions never run
- [ ] Ledger records every action; undo works for all three write types
- [ ] Primary LLM failure triggers fallback without breaking the flow
- [ ] Send-email and browser write tools are not available anywhere in the code path
- [ ] Runs locally on free tiers with documented setup

## 8.6 Testing checklist

Unit: schema validation, tier overwrite, blocked tools, allowlist matching, Trust Dial modes, router failover, undo handlers (mocked).
Integration: each MCP server returns a real result; full flow on the demo account; repeat 5 times without failure.
Adversarial: an email containing instructions to send data; a plan with an unknown tool name; malformed JSON from the LLM; expired OAuth token.

## 8.7 Coding conventions

- Python: type hints, Pydantic models, small modules, async where calling MCP or LLMs.
- Log every tool call and its decision (allowed, blocked, needs approval).
- Return clear error messages to the UI; never swallow exceptions silently.
- Keep MCP server names and tool names configurable, since they differ between servers and versions.
- Prefer simple, readable code over cleverness. This is a 48-hour build.

## 8.8 When something is ambiguous

Choose the **safer** option (read-only, ask the user, draft instead of send), note the decision in a `DECISIONS.md` file, and keep going.
