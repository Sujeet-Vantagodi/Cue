# 03. Tech Stack

Summary: everything runs on free tiers or open source. **Verify every quota and server status before the hackathon starts, because free tiers and MCP server availability change.**

## 3.1 Stack table

| Layer | Choice | Why | Free? |
|---|---|---|---|
| Language (backend) | Python 3.11+ | Fast to build, MCP Python SDK, strong LLM libraries | Yes |
| API framework | FastAPI + Uvicorn | Async, easy WebSocket, auto docs | Yes |
| MCP client | Official `mcp` Python SDK | Connects to servers over stdio or Streamable HTTP | Yes |
| Validation | Pydantic v2 | Enforces the plan schema | Yes |
| Database | SQLite (via SQLModel or plain `sqlite3`) | Zero setup | Yes |
| Frontend | React + Vite (or Next.js) + Tailwind | Fast UI iteration | Yes |
| Primary LLM | Gemini API (free tier) | Free, supports tool/structured output | Free tier, check limits |
| Fallback LLM | Second hosted free-tier provider **or** a local model via Ollama | Failover story | Free; local is limited by RTX 4050 VRAM |
| Gmail | Google Gmail MCP server (check current preview status) | Search/read/draft | Free, needs OAuth |
| Calendar | Google Calendar MCP server | Create events | Free, needs OAuth |
| Notion | Official Notion MCP server (hosted) or Notion API token | Checklist pages | Free plan |
| Web search | DuckDuckGo MCP server (keyless), Tavily/Exa as fallbacks | No-cost search chain | Free, rate-limited |
| Browser | Playwright MCP (Chromium, headless) | Reads JS-rendered pages | Free, open source |
| Hosting | Local machine for demo | No deployment risk | Free |

## 3.2 Integration fallback plan

Some MCP servers (notably Google Workspace ones) were in developer preview and need manual Google Cloud setup, and OAuth tokens can expire quickly. Mitigations:

1. Set up Google Cloud OAuth credentials in the **first 3 hours**, not at the end.
2. If a Google MCP server is unstable, fall back to a gateway such as Zapier MCP (free plan) **or** wrap the Google APIs in a small custom MCP server.
3. Keep a refresh-token flow so the demo does not die on token expiry.

## 3.3 Search provider chain

```
1. DuckDuckGo MCP (keyless)       -> may hit rate limits or CAPTCHAs on heavy use
2. Tavily MCP (free key)          -> free monthly credits, check current amount
3. Exa MCP (free plan)            -> casual use limits
```

Cache every search result in SQLite (query hash -> results). During the demo, pre-warm the cache for the demo scenarios.

## 3.4 Dual-LLM setup

- Interface: `call_llm(messages, schema)` in `backend/app/llm/router.py`.
- Primary and fallback are chosen by environment variables (`LLM_PRIMARY`, `LLM_FALLBACK`).
- Local fallback: small models (for example 7B class via Ollama) fit an RTX 4050 laptop, but their tool-calling and JSON reliability is weaker. Use `schema` repair prompts and keep the fallback prompts simpler.
- Always test both providers on the full demo flow before the event ends.

## 3.5 Environment variables (`.env.example`)

```
LLM_PRIMARY=gemini
LLM_FALLBACK=ollama
GEMINI_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
NOTION_TOKEN=
TAVILY_API_KEY=
EXA_API_KEY=
BROWSER_ALLOWLIST=irctc.co.in,*.gov.in,<company-domain>
TRUST_DEFAULT=ask
```

## 3.6 Suggested repository layout

See doc 08 for the full tree.

Next: [`04-GUARDRAILS-AND-SAFETY.md`](04-GUARDRAILS-AND-SAFETY.md)
