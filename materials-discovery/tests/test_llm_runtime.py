from __future__ import annotations

import importlib

import pytest

from materials_discovery.common.schema import BackendConfig, LlmGenerateConfig
from materials_discovery.llm.runtime import (
    AnthropicApiLlmAdapter,
    MockLlmAdapter,
    OpenAICompatLlmAdapter,
    resolve_llm_adapter,
    validate_llm_adapter_ready,
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


def test_resolve_llm_adapter_returns_openai_compat_adapter() -> None:
    adapter = resolve_llm_adapter(
        "real",
        adapter="openai_compat_v1",
        backend=BackendConfig(
            mode="real",
            llm_adapter="openai_compat_v1",
            llm_provider="openai_compat",
            llm_model="materials-local-v1",
            llm_api_base="https://local.example/v1/",
            llm_request_timeout_s=91.0,
            llm_probe_timeout_s=7.0,
            llm_probe_path="health",
        ),
    )

    assert isinstance(adapter, OpenAICompatLlmAdapter)
    assert adapter.api_base == "https://local.example/v1"
    assert adapter.request_timeout_s == 91.0
    assert adapter.probe_timeout_s == 7.0
    assert adapter.probe_path == "/health"


def test_openai_compat_adapter_prefers_message_content(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeResponse:
        status_code = 200
        text = ""

        def json(self) -> dict:
            return {"choices": [{"message": {"content": "label local.message\n"}}]}

    class _FakeHttpx:
        @staticmethod
        def post(*args, **kwargs):
            return _FakeResponse()

    monkeypatch.setattr(
        "materials_discovery.llm.runtime.importlib.import_module",
        lambda name: _FakeHttpx() if name == "httpx" else importlib.import_module(name),
    )
    adapter = OpenAICompatLlmAdapter(
        provider="openai_compat",
        model="materials-local-v1",
        api_base="https://local.example",
    )

    assert adapter.generate(_request()) == "label local.message\n"


def test_openai_compat_adapter_accepts_text_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeResponse:
        status_code = 200
        text = ""

        def json(self) -> dict:
            return {"choices": [{"text": "label local.text\n"}]}

    class _FakeHttpx:
        @staticmethod
        def post(*args, **kwargs):
            return _FakeResponse()

    monkeypatch.setattr(
        "materials_discovery.llm.runtime.importlib.import_module",
        lambda name: _FakeHttpx() if name == "httpx" else importlib.import_module(name),
    )
    adapter = OpenAICompatLlmAdapter(
        provider="openai_compat",
        model="materials-local-v1",
        api_base="https://local.example",
    )

    assert adapter.generate(_request()) == "label local.text\n"


def test_validate_llm_adapter_ready_uses_default_models_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    class _FakeResponse:
        status_code = 200
        text = ""

        def json(self) -> dict:
            return {"data": [{"id": "materials-local-v1"}]}

    class _FakeHttpx:
        @staticmethod
        def get(url: str, *, timeout: float):
            seen["url"] = url
            seen["timeout"] = timeout
            return _FakeResponse()

    monkeypatch.setattr(
        "materials_discovery.llm.runtime.importlib.import_module",
        lambda name: _FakeHttpx() if name == "httpx" else importlib.import_module(name),
    )
    adapter = OpenAICompatLlmAdapter(
        provider="openai_compat",
        model="materials-local-v1",
        api_base="https://local.example",
        probe_timeout_s=9.0,
    )

    validate_llm_adapter_ready(
        adapter,
        adapter_key="openai_compat_v1",
        requested_lane="specialized_materials",
        resolved_lane="specialized_materials",
    )

    assert seen == {"url": "https://local.example/v1/models", "timeout": 9.0}


def test_validate_llm_adapter_ready_reports_connectivity_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeHttpx:
        @staticmethod
        def get(url: str, *, timeout: float):
            raise RuntimeError(f"cannot connect to {url} in {timeout}s")

    monkeypatch.setattr(
        "materials_discovery.llm.runtime.importlib.import_module",
        lambda name: _FakeHttpx() if name == "httpx" else importlib.import_module(name),
    )
    adapter = OpenAICompatLlmAdapter(
        provider="openai_compat",
        model="materials-local-v1",
        api_base="https://local.example",
    )

    with pytest.raises(
        RuntimeError,
        match="requested lane 'specialized_materials'.*https://local.example/v1/models.*already running",
    ):
        validate_llm_adapter_ready(
            adapter,
            adapter_key="openai_compat_v1",
            requested_lane="specialized_materials",
            resolved_lane="specialized_materials",
        )
