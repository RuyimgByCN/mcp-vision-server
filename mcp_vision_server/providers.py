"""Provider presets for OpenAI-compatible vision APIs."""

from __future__ import annotations

DEFAULT_PROVIDER = "zhipu"

# provider_key -> {name, base_url, model, api_key_env, website}
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
