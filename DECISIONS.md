# Decisions

## 2026-11-24: Start with a local adapter boundary

The first implementation keeps integrations behind the API and records execution through a local adapter. This makes the safety core and UI runnable before OAuth/MCP credentials exist. Real MCP providers can be connected behind the same executor boundary without changing the approval contract.

## 2026-11-24: Use deterministic extraction for the first vertical slice

The planner currently handles the three documented demo events with lightweight extraction. The LLM router is intentionally the next seam: adding a provider must return the existing Pydantic `Plan`, and must not receive direct write-tool access.
