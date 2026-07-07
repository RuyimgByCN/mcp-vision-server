"""Vision MCP server exposing OpenAI-compatible vision models.

Any MCP client can call this server to analyze screenshots, recognize image
content, read text, answer visual questions, or restore UI from mockups.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP
from openai import OpenAI

from mcp_vision_server.config import resolve_config
from mcp_vision_server.image import normalize_image
from mcp_vision_server.providers import PROVIDERS

mcp = FastMCP("vision")


@mcp.tool()
def list_providers() -> str:
    """List all supported provider presets as a JSON array."""
    return json.dumps(
        [
            {
                "key": key,
                "name": preset["name"],
                "model": preset["model"],
                "website": preset["website"],
            }
            for key, preset in PROVIDERS.items()
        ],
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def analyze_image(
    image: str,
    prompt: str = "请详细描述这张图片。",
    image_type: str = "auto",
    provider: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """Analyze or understand an image.

    Use this tool when an MCP client needs image understanding, screenshot
    analysis, OCR-like text recognition, visual Q&A, or UI restoration.
    """
    final_base, final_key, final_model = resolve_config(
        provider=provider, base_url=base_url, api_key=api_key, model=model
    )
    if not final_key:
        return (
            "[错误] 未配置 API key。请设置环境变量 VISION_API_KEY,"
            "或传 provider 参数使用供应商预设,"
            "或直接传 api_key 参数。"
        )

    url = normalize_image(image, image_type)
    if url.startswith("[错误]"):
        return url

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": url}},
            ],
        }
    ]

    try:
        client = OpenAI(base_url=final_base, api_key=final_key)
        resp = client.chat.completions.create(
            model=final_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as exc:  # noqa: BLE001 - MCP tools should return readable errors.
        return (
            f"[错误] API 调用失败:{exc}。请检查 base_url / api_key / model 是否正确。"
        )

    content = resp.choices[0].message.content
    if not content:
        return "[警告] 模型未返回内容。"
    return content


def main() -> None:
    """Run the MCP server with stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()
