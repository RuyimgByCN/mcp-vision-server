# mcp-vision-server

[![PyPI](https://img.shields.io/pypi/v/RuyimgBy-mcp-vision-server?label=PyPI&color=blue)](https://pypi.org/project/RuyimgBy-mcp-vision-server/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Personal%20Use%20Only-orange)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-6E29F6)](https://modelcontextprotocol.io/)

一个面向所有 OpenAI 兼容视觉模型的 MCP 服务。

只需要配置一次，就可以在 OpenAI、DeepSeek、OpenRouter、智谱、百炼、SiliconFlow 等兼容供应商之间复用同一个 `analyze_image` 工具。它适用于 Claude Code、Codex、Cursor、Zed 以及任何 MCP 客户端。

## 为什么使用 mcp-vision-server？

- ✅ **适用于任何 MCP 客户端** —— Claude Code、Codex、Cursor、Zed 等都可以接入。
- ✅ **支持多家视觉模型供应商** —— 切换供应商时不需要改 prompt 或工具调用方式。
- ✅ **统一 API** —— 一个 `analyze_image` 工具即可对接所有 OpenAI 兼容视觉端点。
- ✅ **灵活的图片输入** —— 自动识别 URL、本地文件、Base64 字符串。
- ✅ **支持多层覆盖配置** —— 可通过环境变量全局配置，也可在单次工具调用中覆盖。

## 快速开始

1. 安装服务。
2. 设置供应商和 API key。
3. 把 MCP server 添加到你的客户端。
4. 直接询问：

```text
描述这张截图。
```

如果配置正确，MCP 客户端会自动调用 `analyze_image`，并返回视觉模型的文本回答。

## 功能

- 单一 `analyze_image` 工具，接口一致。
- 支持 URL、本地文件、Base64 三种图片输入。
- 内置 14 个供应商预设。
- 可通过 `VISION_PROVIDER` 或 `provider` 参数切换供应商。
- 支持环境变量级别和单次请求级别的配置覆盖。

## 示例

让 MCP 客户端分析一张图片：

```text
分析这张截图，并告诉我这是什么界面。
```

客户端会调用 MCP 工具：

```json
{
  "tool": "analyze_image",
  "arguments": {
    "image": "/path/to/screenshot.png",
    "prompt": "分析这张截图，并告诉我这是什么界面。"
  }
}
```

服务会自动规范化图片输入，将请求发送到当前选中的 OpenAI 兼容视觉供应商，并把文本结果返回给 MCP 客户端。

## 供应商

内置预设可以快速接入常见 OpenAI 兼容视觉端点：

| 供应商 | Preset |
|---|---|
| 智谱 | `zhipu` |
| 阿里百炼 / DashScope | `bailian` |
| DeepSeek | `deepseek` |
| OpenAI | `openai` |
| SiliconFlow | `siliconflow` |
| OpenRouter | `openrouter` |
| 火山方舟 / Volcengine | `ark` |
| 阶跃星辰 | `stepfun` |
| Kimi / Moonshot | `kimi` |
| MiniMax | `minimax` |
| ModelScope | `modelscope` |
| NVIDIA NIM | `nvidia` |
| Novita AI | `novita` |

如果供应商不在预设列表中，也可以通过 `VISION_BASE_URL`、`VISION_API_KEY`、`VISION_MODEL` 手动接入任何 OpenAI 兼容视觉端点。

## 安装与运行

依赖 Python ≥ 3.10、[uv](https://docs.astral.sh/uv/)。

```bash
cd mcp-vision-server
uv sync                  # 安装依赖
uv run pytest -v         # 跑测试
uv run ruff check .      # 代码检查
uv run mcp-vision-server # 启动 stdio server
```

## 配置

### 方式一：供应商预设（推荐）

```bash
export VISION_PROVIDER=zhipu     # 默认
export VISION_API_KEY=你的key
```

完整预设列表见 [供应商](#供应商)。

也可用供应商专属环境变量兜底，例如 `DASHSCOPE_API_KEY`、`OPENAI_API_KEY`。

### 方式二：手动指定

| 变量 | 必填 | 说明 |
|---|---|---|
| `VISION_API_KEY` | 是 | API key |
| `VISION_BASE_URL` | 否 | OpenAI 兼容端点 |
| `VISION_MODEL` | 否 | 模型名 |

工具参数（每次调用可覆盖，优先级高于环境变量）：`image`、`prompt`、`image_type`、`provider`、`base_url`、`api_key`、`model`、`temperature`、`max_tokens`。

## MCP 客户端注册

### Claude Code（`.mcp.json`）

```json
{
  "mcpServers": {
    "vision": {
      "command": "uv",
      "args": ["run", "--directory", "/绝对路径/mcp-vision-server", "mcp-vision-server"],
      "env": {
        "VISION_PROVIDER": "zhipu",
        "VISION_API_KEY": "your_key"
      }
    }
  }
}
```

### Claude Code 插件安装

```bash
# PyPI 发布后
claude plugins install RuyimgByCN/mcp-vision-server

# 本地测试
claude plugins install /path/to/mcp-vision-server
```

仓库自带 [`.claude-plugin.json`](.claude-plugin.json) 清单文件，`claude plugins install` 会自动读取。

### Codex（OpenAI Codex CLI）

编辑 `~/.codex/config.toml`：

```toml
[mcp_servers.vision]
command = "uvx"
args = ["mcp-vision-server"]
env = { VISION_PROVIDER = "zhipu", VISION_API_KEY = "your_key" }
```

本地开发：

```toml
[mcp_servers.vision]
command = "uv"
args = ["run", "--directory", "/绝对路径/mcp-vision-server", "mcp-vision-server"]
env = { VISION_PROVIDER = "zhipu", VISION_API_KEY = "your_key" }
```

### Cursor / 其它 `uvx` 客户端

改 `command` 为 `uvx`，`args` 改成 `["--from", "/绝对路径/mcp-vision-server", "mcp-vision-server"]`，`env` 同上。

## 切换供应商示例

```json
// 阿里百炼
"env": { "VISION_PROVIDER": "bailian", "VISION_API_KEY": "你的key" }

// OpenAI
"env": { "VISION_PROVIDER": "openai", "VISION_API_KEY": "sk-xxx" }

// 完全自定义
"env": {
  "VISION_BASE_URL": "https://your-endpoint/v1",
  "VISION_API_KEY": "your_key",
  "VISION_MODEL": "your-model"
}
```

## 架构

```text
MCP Client（Claude Code / Codex / Cursor / Zed）
        │
        ▼
mcp-vision-server
        │
        ├── mcp_vision_server/server.py     # MCP 工具入口
        ├── mcp_vision_server/config.py     # 环境变量 / provider / 参数解析
        ├── mcp_vision_server/image.py      # URL / 文件 / Base64 规范化
        └── mcp_vision_server/providers.py  # 供应商预设
        │
        ▼
OpenAI-compatible Vision API
        │
        ▼
视觉模型返回结果
```

## FAQ

### 为什么不直接调用视觉模型供应商？

这个服务给 MCP 客户端提供了一个统一、可复用的视觉工具。切换供应商时，不需要改客户端 prompt、MCP 工具名或客户端侧集成代码。

### 可以使用未列出的供应商吗？

可以。只要是 OpenAI 兼容的视觉端点，都可以通过 `VISION_BASE_URL`、`VISION_API_KEY`、`VISION_MODEL` 手动配置。

### 可以在单次请求中覆盖供应商吗？

可以。使用 `provider`、`base_url`、`api_key` 或 `model` 工具参数即可覆盖环境变量配置，只对当前调用生效。

### 支持哪些图片输入格式？

服务支持图片 URL、本地文件路径、Base64 字符串。输入类型可以自动识别，也可以通过 `image_type` 显式指定。

## 开发

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format .
uv run pytest -v
uv build
uv run twine check dist/*
```

## 发布检查清单

1. 更新 `pyproject.toml` 中的版本号。
2. 运行 `uv run ruff check .`、`uv run pytest -v`、`uv build`、`uv run twine check dist/*`。
3. 创建并推送版本 tag，例如 `v0.1.2`。
4. 通过 GitHub Actions trusted publishing 发布到 PyPI。

## Roadmap

- 在更多稳定的 OpenAI 兼容视觉端点可用后，继续增加供应商预设。
- 补充 Claude Code、Codex、Cursor 等 MCP 客户端的更完整示例。
- 如果 MCP 客户端体验确实受益，再考虑增加可选流式响应支持。
- 只有当供应商需要自定义请求逻辑时，才拆分 provider-specific 插件。

## 关于

**作者：** [RuyimgByCN](https://github.com/RuyimgByCN)

**开源协议：** 个人使用免费，**禁止商用**。详见 [LICENSE](LICENSE)。商业授权请联系作者。

**English:** Free for personal use. Commercial use prohibited. See [README.md](README.md)。
