from __future__ import annotations

import importlib

import pytest

from materials_discovery.common.schema import BackendConfig, LlmGenerateConfig
from materials_discovery.llm.runtime import (
    AnthropicApiLlmAdapter,
    MockLlmAdapter,
    resolve_llm_adapter,
)
from materials_discovery.llm.schema import LlmGenerationRequest


def _request() -> LlmGenerationRequest:
    return LlmGenerationRequest(
        system="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        composition_bounds={"Al": {"min": 0.6, "max": 0.8}},
        prompt_text="emit only zomic",
        temperature=0.1,
        max_tokens=128,
    )


def test_resolve_llm_adapter_returns_mock_adapter() -> None:
    adapter = resolve_llm_adapter(
        "mock",
        backend=BackendConfig(mode="mock"),
        llm_generate=LlmGenerateConfig(fixture_outputs=["first"]),
    )

    assert isinstance(adapter, MockLlmAdapter)


def test_mock_adapter_emits_fixture_outputs_in_deterministic_order() -> None:
    adapter = MockLlmAdapter(["first", "second"])

    assert adapter.generate(_request()) == "first"
    assert adapter.generate(_request()) == "second"


def test_anthropic_api_key_is_checked_at_generate_time(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = resolve_llm_adapter(
        "real",
        adapter="anthropic_api_v1",
        backend=BackendConfig(
            mode="real",
            llm_adapter="anthropic_api_v1",
            llm_provider="anthropic",
            llm_model="claude-sonnet",
        ),
    )

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        adapter.generate(_request())


def test_httpx_is_imported_lazily_inside_generate(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    class _FakeResponse:
        status_code = 200
        text = ""

        def json(self) -> dict:
            return {"content": [{"type": "text", "text": "branch move blue"}]}

    class _FakeHttpx:
        @staticmethod
        def post(*args, **kwargs):
            return _FakeResponse()

    def _fake_import(name: str):
        calls.append(name)
        if name == "httpx":
            return _FakeHttpx()
        return importlib.import_module(name)

    adapter = AnthropicApiLlmAdapter(provider="anthropic", model="claude-sonnet")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr("materials_discovery.llm.runtime.importlib.import_module", _fake_import)

    assert calls == []
    assert adapter.generate(_request()) == "branch move blue"
    assert calls == ["httpx"]


def test_anthropic_adapter_respects_api_base_override(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, str] = {}

    class _FakeResponse:
        status_code = 200
        text = ""

        def json(self) -> dict:
            return {"content": [{"type": "text", "text": "orbit A"}]}

    class _FakeHttpx:
        @staticmethod
        def post(url: str, **kwargs):
            seen["url"] = url
            return _FakeResponse()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(
        "materials_discovery.llm.runtime.importlib.import_module",
        lambda name: _FakeHttpx() if name == "httpx" else importlib.import_module(name),
    )
    adapter = AnthropicApiLlmAdapter(
        provider="anthropic",
        model="claude-sonnet",
        api_base="https://example.test/api",
    )

    assert adapter.generate(_request()) == "orbit A"
    assert seen["url"] == "https://example.test/api/v1/messages"


def test_anthropic_adapter_surfaces_status_and_body_detail(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeResponse:
        status_code = 429
        text = "rate limit"

        def json(self) -> dict:
            return {}

    class _FakeHttpx:
        @staticmethod
        def post(*args, **kwargs):
            return _FakeResponse()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(
        "materials_discovery.llm.runtime.importlib.import_module",
        lambda name: _FakeHttpx() if name == "httpx" else importlib.import_module(name),
    )

    adapter = AnthropicApiLlmAdapter(provider="anthropic", model="claude-sonnet")
    with pytest.raises(RuntimeError, match="429: rate limit"):
        adapter.generate(_request())
