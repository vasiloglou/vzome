from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from typing import Any, Protocol

from materials_discovery.common.schema import BackendConfig, LlmGenerateConfig
from materials_discovery.llm.schema import LlmGenerationRequest


class LlmAdapter(Protocol):
    def generate(self, request: LlmGenerationRequest) -> str:
        ...


@dataclass
class MockLlmAdapter:
    fixture_outputs: list[str]
    _cursor: int = field(default=0, init=False, repr=False)

    def generate(self, request: LlmGenerationRequest) -> str:  # pragma: no cover - exercised via tests
        del request
        if not self.fixture_outputs:
            raise ValueError("fixture_outputs must not be empty")
        output = self.fixture_outputs[self._cursor % len(self.fixture_outputs)]
        self._cursor += 1
        return output


@dataclass
class AnthropicApiLlmAdapter:
    provider: str
    model: str
    api_base: str | None = None

    def generate(self, request: LlmGenerationRequest) -> str:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required for anthropic_api_v1")

        httpx = importlib.import_module("httpx")
        endpoint = f"{(self.api_base or 'https://api.anthropic.com').rstrip('/')}/v1/messages"
        payload = {
            "model": self.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": [{"role": "user", "content": request.prompt_text}],
        }
        response = httpx.post(
            endpoint,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=30.0,
        )

        if response.status_code < 200 or response.status_code >= 300:
            body = response.text.strip()
            detail = body[:240] if body else "no response body"
            raise RuntimeError(
                f"anthropic_api_v1 request failed with status {response.status_code}: {detail}"
            )

        data = response.json()
        content = data.get("content")
        if not isinstance(content, list):
            raise RuntimeError("anthropic_api_v1 response did not contain a content list")
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    return text
        raise RuntimeError("anthropic_api_v1 response did not contain a text block")


def resolve_llm_adapter(
    mode: str,
    adapter: str | None = None,
    *,
    backend: BackendConfig | None = None,
    llm_generate: LlmGenerateConfig | None = None,
) -> LlmAdapter:
    effective_adapter = adapter
    if effective_adapter is None and backend is not None:
        effective_adapter = backend.llm_adapter

    if mode == "mock":
        if effective_adapter in (None, "llm_fixture_v1"):
            fixture_outputs = [] if llm_generate is None else list(llm_generate.fixture_outputs)
            return MockLlmAdapter(fixture_outputs=fixture_outputs)
        raise ValueError(f"unsupported mock llm adapter: {effective_adapter}")

    if mode == "real":
        if effective_adapter != "anthropic_api_v1":
            raise ValueError(f"unsupported real llm adapter: {effective_adapter}")
        if backend is None:
            raise ValueError("backend config is required for anthropic_api_v1")
        if backend.llm_provider is None:
            raise ValueError("backend.llm_provider must be set for anthropic_api_v1")
        if backend.llm_model is None:
            raise ValueError("backend.llm_model must be set for anthropic_api_v1")
        return AnthropicApiLlmAdapter(
            provider=backend.llm_provider,
            model=backend.llm_model,
            api_base=backend.llm_api_base,
        )

    raise ValueError(f"unsupported llm mode: {mode}")
