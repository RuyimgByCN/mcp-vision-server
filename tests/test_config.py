from mcp_vision_server.config import resolve_config
from mcp_vision_server.providers import PROVIDERS

DEFAULT_BASE = PROVIDERS["zhipu"]["base_url"]
DEFAULT_MODEL = PROVIDERS["zhipu"]["model"]


def _clear_env(monkeypatch):
    """Clear related env vars to keep tests isolated."""
    for key in (
        "VISION_PROVIDER",
        "VISION_BASE_URL",
        "VISION_API_KEY",
        "VISION_MODEL",
        "GLM_VISION_API_KEY",
        "DASHSCOPE_API_KEY",
        "DEEPSEEK_API_KEY",
        "OPENAI_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)


def test_defaults_when_nothing_set(monkeypatch):
    _clear_env(monkeypatch)
    base_url, api_key, model = resolve_config(api_key="sk-test")
    assert base_url == DEFAULT_BASE
    assert api_key == "sk-test"
    assert model == DEFAULT_MODEL


def test_provider_switch(monkeypatch):
    _clear_env(monkeypatch)
    base_url, api_key, model = resolve_config(provider="bailian", api_key="sk-bl")
    assert base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert api_key == "sk-bl"
    assert model == "qwen-vl-max"


def test_provider_via_env(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("VISION_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    base_url, api_key, model = resolve_config()
    assert base_url == "https://api.openai.com/v1"
    assert api_key == "sk-openai"
    assert model == "gpt-4o"


def test_params_override_provider(monkeypatch):
    _clear_env(monkeypatch)
    base_url, api_key, model = resolve_config(
        provider="zhipu",
        base_url="https://custom.example.com/v1",
        api_key="sk-custom",
        model="custom-model",
    )
    assert base_url == "https://custom.example.com/v1"
    assert api_key == "sk-custom"
    assert model == "custom-model"


def test_vision_api_key_overrides_provider(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("VISION_PROVIDER", "bailian")
    monkeypatch.setenv("VISION_API_KEY", "sk-global")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-dashscope")
    base_url, api_key, model = resolve_config()
    assert base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert api_key == "sk-global"


def test_missing_api_key_returns_none(monkeypatch):
    _clear_env(monkeypatch)
    base_url, api_key, model = resolve_config()
    assert base_url == DEFAULT_BASE
    assert api_key is None
    assert model == DEFAULT_MODEL


def test_unknown_provider_falls_back_empty(monkeypatch):
    _clear_env(monkeypatch)
    base_url, api_key, model = resolve_config(provider="nonexistent")
    assert base_url is None
    assert api_key is None
    assert model is None


def test_all_providers_have_required_keys():
    for key, preset in PROVIDERS.items():
        assert "name" in preset, f"{key}: missing name"
        assert "base_url" in preset, f"{key}: missing base_url"
        assert "model" in preset, f"{key}: missing model"
        assert "api_key_env" in preset, f"{key}: missing api_key_env"
        assert "website" in preset, f"{key}: missing website"
