import json
from types import SimpleNamespace

import mcp_vision_server.server as server


def test_list_providers_returns_json_array():
    providers = json.loads(server.list_providers())
    assert isinstance(providers, list)
    assert {"key", "name", "model", "website"}.issubset(providers[0])
    assert any(provider["key"] == "zhipu" for provider in providers)


def test_analyze_image_missing_api_key(monkeypatch):
    monkeypatch.delenv("VISION_API_KEY", raising=False)
    monkeypatch.delenv("GLM_VISION_API_KEY", raising=False)

    result = server.analyze_image("https://example.com/a.png")

    assert result.startswith("[错误] 未配置 API key")


def test_analyze_image_invalid_image_returns_normalization_error():
    result = server.analyze_image("not a valid image", api_key="sk-test")

    assert result.startswith("[错误] 无法自动识别 image 类型")


def test_analyze_image_returns_model_content(monkeypatch):
    captured = {}

    class FakeCompletions:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))]
            )

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured["client"] = kwargs
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(server, "OpenAI", FakeOpenAI)

    result = server.analyze_image(
        image="https://example.com/a.png",
        prompt="describe",
        provider="openai",
        api_key="sk-test",
        temperature=0.1,
        max_tokens=32,
    )

    assert result == "ok"
    assert captured["client"] == {
        "base_url": "https://api.openai.com/v1",
        "api_key": "sk-test",
    }
    assert captured["model"] == "gpt-4o"
    assert captured["temperature"] == 0.1
    assert captured["max_tokens"] == 32
    assert captured["messages"][0]["content"] == [
        {"type": "text", "text": "describe"},
        {"type": "image_url", "image_url": {"url": "https://example.com/a.png"}},
    ]


def test_analyze_image_api_exception_returns_readable_error(monkeypatch):
    class FakeCompletions:
        @staticmethod
        def create(**kwargs):
            raise RuntimeError("boom")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(server, "OpenAI", FakeOpenAI)

    result = server.analyze_image("https://example.com/a.png", api_key="sk-test")

    assert result.startswith("[错误] API 调用失败:boom")


def test_analyze_image_empty_model_content_returns_warning(monkeypatch):
    class FakeCompletions:
        @staticmethod
        def create(**kwargs):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
            )

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(server, "OpenAI", FakeOpenAI)

    result = server.analyze_image("https://example.com/a.png", api_key="sk-test")

    assert result == "[警告] 模型未返回内容。"
