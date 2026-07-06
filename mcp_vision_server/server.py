"""多模态 vision MCP server — 支持 10+ 供应商预设。

把任意 OpenAI 兼容的 vision 模型暴露为 MCP 工具。
通过 --provider 或 VISION_PROVIDER 环境变量一键切换供应商，
也可手动传 base_url/api_key/model 使用任意兼容平台。
"""

from __future__ import annotations

import base64
import mimetypes
import os
import re
from typing import Optional

from mcp.server.fastmcp import FastMCP
from openai import OpenAI

# ---------------------------------------------------------------------------
# 供应商预设
# ---------------------------------------------------------------------------

# 裸 base64 合法字符集 + 最小长度(过滤掉普通短字符串)
_B64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
_B64_MIN_LEN = 64

# 供应商预设: provider_key → {name, base_url, model, api_key_env, website}
PROVIDERS: dict[str, dict[str, str]] = {
    "zhipu": {
        "name": "智谱 GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model": "glm-5v-turbo",
        "api_key_env": "GLM_VISION_API_KEY",
        "website": "https://open.bigmodel.cn",
    },
    "bailian": {
        "name": "阿里百炼",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-vl-max",
        "api_key_env": "DASHSCOPE_API_KEY",
        "website": "https://bailian.console.aliyun.com",
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
        "website": "https://platform.deepseek.com",
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
        "website": "https://platform.openai.com",
    },
    "siliconflow": {
        "name": "SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "model": "Qwen/Qwen2.5-VL-72B-Instruct",
        "api_key_env": "SILICONFLOW_API_KEY",
        "website": "https://siliconflow.cn",
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-4o",
        "api_key_env": "OPENROUTER_API_KEY",
        "website": "https://openrouter.ai",
    },
    "ark": {
        "name": "火山方舟",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-vision-pro-32k",
        "api_key_env": "ARK_API_KEY",
        "website": "https://www.volcengine.com/product/ark",
    },
    "stepfun": {
        "name": "阶跃星辰",
        "base_url": "https://api.stepfun.com/v1",
        "model": "step-1v-8k",
        "api_key_env": "STEPFUN_API_KEY",
        "website": "https://platform.stepfun.com",
    },
    "kimi": {
        "name": "Kimi (月之暗面)",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "kimi-k2.7-code",
        "api_key_env": "MOONSHOT_API_KEY",
        "website": "https://platform.kimi.com",
    },
    "minimax": {
        "name": "MiniMax",
        "base_url": "https://api.minimaxi.com/v1",
        "model": "MiniMax-M2.7",
        "api_key_env": "MINIMAX_API_KEY",
        "website": "https://platform.minimaxi.com",
    },
    "modelscope": {
        "name": "ModelScope",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "model": "Qwen/QVQ-72B-Preview",
        "api_key_env": "MODELSCOPE_API_KEY",
        "website": "https://modelscope.cn",
    },
    "nvidia": {
        "name": "NVIDIA NIM",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "model": "nvidia/llama-3.2-nv-vision-90b-instruct",
        "api_key_env": "NVIDIA_API_KEY",
        "website": "https://build.nvidia.com",
    },
    "novita": {
        "name": "Novita AI",
        "base_url": "https://api.novita.ai/v3/openai",
        "model": "qwen/qwen-2.5-vl-72b-instruct",
        "api_key_env": "NOVITA_API_KEY",
        "website": "https://novita.ai",
    },
}


def normalize_image(image: str, image_type: str = "auto") -> str:
    """把图像输入归一化为 OpenAI vision message 中 image_url.url 的值。

    - URL → 原样返回
    - 本地文件路径 → 读取文件,编码为 data:<mime>;base64,<...>
    - 裸 base64 → 补 data:image/png;base64, 前缀
    - 无法识别 → 返回 "[错误] ..." 字符串(不抛异常)

    image_type 可显式指定为 "url"/"file"/"base64" 跳过自动检测。
    """
    img = image.strip()
    kind = image_type.strip().lower()

    def _as_url() -> str:
        return img

    def _as_file() -> str:
        if not os.path.exists(img):
            return f"[错误] 文件不存在:{img}"
        mime, _ = mimetypes.guess_type(img)
        if not mime:
            mime = "image/png"
        with open(img, "rb") as fh:
            data = base64.b64encode(fh.read()).decode("ascii")
        return f"data:{mime};base64,{data}"

    def _as_base64() -> str:
        return f"data:image/png;base64,{img}"

    if kind == "url":
        return _as_url()
    if kind == "file":
        return _as_file()
    if kind == "base64":
        return _as_base64()

    # auto
    if img.startswith(("http://", "https://")):
        return _as_url()
    if os.path.exists(img):
        return _as_file()
    if len(img) >= _B64_MIN_LEN and _B64_RE.match(img):
        return _as_base64()
    return (
        "[错误] 无法自动识别 image 类型。"
        "请显式传 image_type 为 'url' / 'file' / 'base64'。"
    )


DEFAULT_PROVIDER = "zhipu"


def resolve_config(
    provider: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> tuple[str | None, str | None, str | None]:
    """解析生效的 base_url/api_key/model。

    优先级: 显式参数 > 环境变量 > 供应商预设默认值。
    - provider: 供应商 key(如 "zhipu"/"bailian"/"openai"),缺省读 VISION_PROVIDER 或 "zhipu"
    - 显式传 base_url/api_key/model 时覆盖供应商预设
    api_key 无默认,缺失时返回 None(由 analyze_image 报错)。
    """
    provider_key = provider or os.environ.get("VISION_PROVIDER") or DEFAULT_PROVIDER
    preset = PROVIDERS.get(provider_key, {})

    base_url = (
        base_url
        or os.environ.get("VISION_BASE_URL")
        or preset.get("base_url", "")
    )
    api_key = (
        api_key
        or os.environ.get("VISION_API_KEY")
        or os.environ.get(preset.get("api_key_env", ""))
    )
    model = (
        model
        or os.environ.get("VISION_MODEL")
        or preset.get("model", "")
    )
    return base_url or None, api_key or None, model or None


mcp = FastMCP("vision")


@mcp.tool()
def list_providers() -> str:
    """列出所有支持的供应商预设,返回 JSON 数组。"""
    import json

    return json.dumps(
        [
            {"key": k, "name": v["name"], "model": v["model"], "website": v["website"]}
            for k, v in PROVIDERS.items()
        ],
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def analyze_image(
    image: str,
    prompt: str = "请详细描述这张图片。",
    image_type: str = "auto",
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """分析/理解一张图片。当需要看图、分析截图、识别图像内容、读取图中文字、
    UI 还原、视觉问答等任何图像理解任务时调用此工具。

    Args:
        image: 图像来源。可以是图像 URL(http/https)、本地文件路径、
            或裸 base64 字符串。image_type="auto" 时自动识别。
        prompt: 要问模型的问题或指令(如"识别图中文字"、"把这张 UI 还原成代码")。
        image_type: "auto"(默认)/"url"/"file"/"base64"。不确定时用 auto。
        provider: 供应商 key,如 "zhipu"/"bailian"/"openai"。
            缺省读 VISION_PROVIDER 环境变量,再缺省为 "zhipu"。
            传 base_url/api_key/model 时覆盖供应商预设。
        base_url: 平台端点,覆盖供应商预设。
        api_key: API key,覆盖供应商预设。
        model: 模型名,覆盖供应商预设。
        temperature: 采样温度,默认 0.2。
        max_tokens: 最大返回 token 数,默认 1024。

    Returns:
        模型的文本回复。出错时返回以 "[错误]" 开头的人类可读说明。
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
    except Exception as exc:  # noqa: BLE001 — 工具内兜底,不向宿主抛异常
        return f"[错误] API 调用失败:{exc}。请检查 base_url / api_key / model 是否正确。"

    content = resp.choices[0].message.content
    if not content:
        return "[警告] 模型未返回内容。"
    return content


def main() -> None:
    """MCP server 入口(stdio transport)。"""
    mcp.run()


if __name__ == "__main__":
    main()
