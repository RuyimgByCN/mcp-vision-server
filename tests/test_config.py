import mcp_vision_server.server as server_module
from mcp_vision_server.server import PROVIDERS, resolve_config

DEFAULT_BASE = PROVIDERS["zhipu"]["base_url"]
DEFAULT_MODEL = PROVIDERS["zhipu"]["model"]


def _clear_env(monkeypatch):
    """清掉所有相关环境变量,确保测试隔离。"""
    for k in (
        "VISION_PROVIDER",
        "VISION_BASE_URL",
        "VISION_API_KEY",
        "VISION_MODEL",
        "GLM_VISION_API_KEY",
        "DASHSCOPE_API_KEY",
        "DEEPSEEK_API_KEY",
        "OPENAI_API_KEY",
    ):
        monkeypatch.delenv(k, raising=False)


def test_defaults_when_nothing_set(monkeypatch):
    _clear_env(monkeypatch)
    base_url, api_key, model = resolve_config(api_key="sk-test")
    assert base_url == DEFAULT_BASE
    assert api_key == "sk-test"
    assert model == DEFAULT_MODEL


def test_provider_switch(monkeypatch):
    """指定 provider 切换供应商预设。"""
    _clear_env(monkeypatch)
    base_url, api_key, model = resolve_config(
        provider="bailian", api_key="sk-bl"
    )
    assert base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert api_key == "sk-bl"
    assert model == "qwen-vl-max"


def test_provider_via_env(monkeypatch):
    """通过 VISION_PROVIDER 环境变量切换。"""
    _clear_env(monkeypatch)
    monkeypatch.setenv("VISION_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    base_url, api_key, model = resolve_config()
    assert base_url == "https://api.openai.com/v1"
    assert api_key == "sk-openai"
    assert model == "gpt-4o"


def test_params_override_provider(monkeypatch):
    """显式参数覆盖供应商预设。"""
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
    """VISION_API_KEY 优先于供应商专属环境变量。"""
    _clear_env(monkeypatch)
    monkeypatch.setenv("VISION_PROVIDER", "bailian")
    monkeypatch.setenv("VISION_API_KEY", "sk-global")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-dashscope")
    base_url, api_key, model = resolve_config()
    assert base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert api_key == "sk-global"


def test_missing_api_key_returns_none(monkeypatch):
    """既无参数也无环境变量时 api_key 为 None。"""
    _clear_env(monkeypatch)
    base_url, api_key, model = resolve_config()
    assert base_url == DEFAULT_BASE
    assert api_key is None
    assert model == DEFAULT_MODEL


def test_unknown_provider_falls_back_empty(monkeypatch):
    """未知 provider key 返回空默认值。"""
    _clear_env(monkeypatch)
    base_url, api_key, model = resolve_config(provider="nonexistent")
    assert base_url is None
    assert api_key is None
    assert model is None


def test_all_providers_have_required_keys():
    """每个供应商预设都有必需的字段。"""
    for key, preset in PROVIDERS.items():
        assert "name" in preset, f"{key}: missing name"
        assert "base_url" in preset, f"{key}: missing base_url"
        assert "model" in preset, f"{key}: missing model"
        assert "api_key_env" in preset, f"{key}: missing api_key_env"
        assert "website" in preset, f"{key}: missing website"