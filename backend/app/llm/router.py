from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Protocol
from urllib import error, request

logger = logging.getLogger("cue.llm")


class Provider(Protocol):
    name: str

    def complete(self, messages: list[dict[str, str]], schema: dict[str, Any] | None = None) -> dict[str, Any]: ...


class MockProvider:
    name = "mock"

    def complete(self, messages: list[dict[str, str]], schema: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"provider": self.name, "content": "{}"}


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-3.8-flash") -> None:
        self.api_key, self.model = api_key, model

    def complete(self, messages: list[dict[str, str]], schema: dict[str, Any] | None = None) -> dict[str, Any]:
        parts = [{"text": f"{item['role']}: {item['content']}"} for item in messages]
        body: dict[str, Any] = {"contents": [{"parts": parts}]}
        if schema:
            body["generationConfig"] = {"responseMimeType": "application/json", "responseSchema": schema}
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = json.dumps(body).encode()
        req = request.Request(endpoint, data=payload, headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key})
        result = None
        for attempt in range(2):
            try:
                with request.urlopen(req, timeout=20) as response:
                    result = json.loads(response.read())
                break
            except error.HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504} or attempt == 1:
                    raise
                time.sleep(1)
        if result is None:
            raise RuntimeError("Gemini returned no response")
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return {"provider": self.name, "content": text}


def _provider(name: str) -> Provider:
    if name == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is required for the Gemini provider")
        return GeminiProvider(key, os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
    return MockProvider()


def call_llm(messages: list[dict[str, str]], schema: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call the primary provider, then fallback; callers receive parsed JSON data."""
    names = [os.getenv("LLM_PRIMARY", "mock"), os.getenv("LLM_FALLBACK", "mock")]
    last_error: Exception | None = None
    failures: list[str] = []
    for name in dict.fromkeys(names):
        try:
            response = _provider(name).complete(messages, schema)
            content = response["content"]
            if isinstance(content, str):
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                parsed = json.loads(content)
            else:
                parsed = content
            if name == "mock" and not parsed:
                raise RuntimeError("mock provider returned empty JSON")
            logger.info("llm provider=%s", name)
            return {"provider": name, "data": parsed}
        except Exception as exc:  # provider failures must activate the next brain
            last_error = exc
            failures.append(f"{name}:{type(exc).__name__}:{str(exc)[:180]}")
            logger.warning("llm provider=%s failed (%s): %s", name, type(exc).__name__, exc)
    raise RuntimeError("all LLM providers failed | " + " | ".join(failures)) from last_error
