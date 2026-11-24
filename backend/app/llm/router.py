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

    def __init__(self, api_key: str, model: str = "gemini-3.6-flash") -> None:
        self.api_key, self.model = api_key, model

    def complete(self, messages: list[dict[str, str]], schema: dict[str, Any] | None = None) -> dict[str, Any]:
        prompt = "\n\n".join(f"{item['role']}: {item['content']}" for item in messages)
        body: dict[str, Any] = {"model": self.model, "input": prompt}
        if schema:
            body["response_format"] = {"type": "text", "mime_type": "application/json", "schema": schema}
        endpoint = "https://generativelanguage.googleapis.com/v1beta/interactions"
        payload = json.dumps(body).encode()
        req = request.Request(endpoint, data=payload, headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key})
        result = None
        for attempt in range(3):
            try:
                with request.urlopen(req, timeout=20) as response:
                    result = json.loads(response.read())
                break
            except error.HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504} or attempt == 2:
                    raise
                time.sleep(2**attempt)
        if result is None:
            raise RuntimeError("Gemini returned no response")
        text_blocks = [
            block
            for step in result.get("steps", [])
            if step.get("type") == "model_output"
            for block in step.get("content", [])
            if block.get("type") == "text"
        ]
        if not text_blocks:
            raise RuntimeError("Gemini interaction returned no text output")
        text = text_blocks[-1]["text"]
        return {"provider": self.name, "content": text}


class OllamaProvider:
    name = "ollama"

    def __init__(self, base_url: str, model: str) -> None:
        if not model:
            raise RuntimeError("OLLAMA_MODEL is required for the Ollama provider")
        self.base_url, self.model = base_url.rstrip("/"), model

    def complete(self, messages: list[dict[str, str]], schema: dict[str, Any] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"model": self.model, "messages": messages, "stream": False, "format": "json"}
        req = request.Request(f"{self.base_url}/api/chat", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
        content = result.get("message", {}).get("content")
        if not content:
            raise RuntimeError("Ollama returned no message content")
        return {"provider": self.name, "content": content}


def _provider(name: str) -> Provider:
    if name == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is required for the Gemini provider")
        return GeminiProvider(key, os.getenv("GEMINI_MODEL", "gemini-3.6-flash"))
    if name == "ollama":
        return OllamaProvider(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), os.getenv("OLLAMA_MODEL", ""))
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
