# 06. Build Timeline (48 Hours)

Summary: about **36 hours of focused work**, about **8 hours of sleep and meals**, and **4 hours of buffer**. Order matters: **integrations and the safety core first, polish last.** Adjust the hour numbers to your actual start time.

## 6.1 Roles (3 people, rename as needed)

- **A (Backend lead):** planner, LLM router, guardrails, ledger
- **B (Integrations):** MCP servers, OAuth, executor, search, Playwright
- **C (Frontend and demo):** UI, Blast Radius, audit log, pitch

If you are 2 people, merge B into A and let C own integration testing.

## 6.2 Hour-by-hour plan

| Hours | Block | Tasks | Owner | Done when |
|---|---|---|---|---|
| 0 to 2 | **Setup** | Create repo, structure, `.env.example`, FastAPI skeleton, Vite app skeleton. Agree on the plan schema (doc 05). Create Google Cloud project, Notion integration, Gemini key. | All | Repo runs, keys obtained |
| 2 to 6 | **Connect MCP servers** (hardest risk first) | Gmail + Calendar OAuth and tool listing; Notion MCP; DuckDuckGo MCP; Playwright MCP. Print each server's real tool names. Write the tool registry mapping. | B | Each server returns one real result from a script |
| 2 to 6 | **LLM router** | `call_llm()`, Gemini provider, fallback provider, JSON schema parsing, repair prompt | A | Both providers return valid plan JSON for a test sentence |
| 2 to 6 | **UI skeleton** | Input box, plan view, mock Blast Radius with fake data | C | UI renders a hardcoded plan |
| 6 to 12 | **Planner and READ pipeline** | Event extraction, plan generation, run READ actions, evidence store, Pydantic validation | A + B | Sentence produces a validated plan with real Gmail and web evidence |
| 6 to 12 | **Guardrail engine** | Registry loader, tier overwrite, Trust Dial, block unknown tools, domain allowlist | A | Unit tests: blocked tools refused, tiers overwritten |
| 6 to 12 | **Blast Radius UI** | Real data, group by app, evidence links, approve/reject per action, Trust Dial control | C | UI shows live plan from backend |
| 12 to 14 | **Checkpoint 1 (mid-point demo)** | Run the full read-only flow end to end | All | Sentence to Blast Radius works with real data |
| 14 to 20 | **Executor and writes** | Calendar create, Notion create, Gmail draft; execute approved actions in dependency order | B | Approved actions appear in the real apps |
| 14 to 20 | **Ledger and undo** | SQLite ledger, receipts, undo for calendar, Notion, drafts | A | Undo removes the created items |
| 14 to 20 | **Audit log UI and receipts** | History page, undo button, status badges | C | Log shows approvals and results |
| 20 to 24 | **Sleep shift 1** (rotate: at least one person always awake) | Light tasks only: docs, README polish, test data | rotating | Everyone rested at least 4 hours |
| 24 to 30 | **Failover and reliability** | Force primary failure and confirm fallback; search provider chain; caching; error states in UI | A + B | Demo survives killed primary LLM |
| 24 to 30 | **Second life event** | Add `moving_out` or `lost_phone` template and test | B | Second event works end to end |
| 24 to 30 | **Safety demo features** | Prompt-injection test email, blocked-tool attempt shown in log, evidence badges | A + C | Injection test is refused and visible |
| 30 to 36 | **Polish** | UI design pass, loading states, empty states, copy, evidence links | C | Looks clean on a projector |
| 30 to 36 | **Hardening** | Token refresh, retry logic, rate-limit handling, pre-warm search cache | B | 5 runs in a row without failure |
| 36 to 40 | **Demo prep** | Prepare demo Gmail with realistic offer-letter email; script (doc 07); record a backup video | All | Backup video recorded |
| 40 to 44 | **Sleep shift 2 and freeze** | Code freeze at hour 40 except critical bug fixes | rotating | No new features after freeze |
| 44 to 48 | **Final rehearsal and submit** | Run the pitch 3 times, check README links, push final repo, submit | All | Submitted with 30+ minutes to spare |

## 6.3 Priority tiers (cut from the bottom if you fall behind)

1. **Must have:** one life event end to end; Gmail read plus draft; Calendar create; Notion create; Blast Radius with approve/reject; guardrails; ledger.
2. **Should have:** undo; dual-LLM failover; evidence trails; web search; Trust Dial.
3. **Nice to have:** Playwright browser reads; second life event; injection-test demo; polished animations.

## 6.4 Risk list and mitigations

| Risk | Mitigation |
|---|---|
| Google OAuth or MCP setup eats hours | Start it in hour 0 to 2; fallback to Zapier MCP or a small custom MCP wrapper |
| Free LLM rate limits during demo | Fallback provider, cached plan for the demo, backup video |
| DuckDuckGo blocks or rate-limits | Search chain plus caching plus pre-warmed results |
| LLM returns invalid JSON | Schema validation plus one repair attempt, simpler fallback prompts |
| Scope creep | Follow the priority tiers; freeze at hour 40 |
| Demo wifi fails | Run locally, backup recorded video, screenshots |

Next: [`07-DEMO-SCRIPT.md`](07-DEMO-SCRIPT.md)
