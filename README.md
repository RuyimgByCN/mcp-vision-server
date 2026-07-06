# mcp-vision-server

> OpenAI-compatible vision MCP server with 14 provider presets.
> 14 个供应商预设的 OpenAI 兼容 vision MCP 服务。

Any MCP client (Claude Code, Codex, Cursor, ZCode…) can call it to "see" images — analyze screenshots, recognize content, read text, answer visual questions, restore UI from mockups.

任何 MCP 客户端接入后，需要"看图"时自动调用 —— 分析截图、识别内容、读图答题、UI 还原。

---

## Features · 功能

- Single tool `analyze_image`: pass an image + prompt, get text response. · 单工具：传图片 + 问题，返回文本回复。
- Three image input types: **URL** / **local file** / **base64 string** (auto-detect). · 三种输入：URL / 本地文件 / base64（自动识别）。
- **14 provider presets**: Zhipu, Bailian, DeepSeek, OpenAI, SiliconFlow, OpenRouter, Ark, StepFun, Kimi, MiniMax, ModelScope, NVIDIA NIM, Novita AI. · 14 个供应商预设。
- Switch providers via `VISION_PROVIDER` env var or `provider` parameter. · 一键切换供应商。
- Override at both **env** and **tool parameter** levels. · 环境变量 + 工具参数两层覆盖。

---

## Install & Run · 安装与运行

Requires Python ≥ 3.10 and [uv](https://docs.astral.sh/uv/). · 依赖 Python ≥ 3.10、uv。

```bash
cd mcp-vision-server
uv sync                  # install deps · 安装依赖
uv run pytest -v         # run tests (optional) · 跑测试
uv run mcp-vision-server # start stdio server · 启动
```

---

## Configuration · 配置

### Option 1: Provider preset (recommended) · 供应商预设

```bash
export VISION_PROVIDER=zhipu     # default · 默认
export VISION_API_KEY=your_key
```

Supported presets: `zhipu` `bailian` `deepseek` `openai` `siliconflow` `openrouter` `ark` `stepfun` `kimi` `minimax` `modelscope` `nvidia` `novita`.

You can also use provider-specific env vars (e.g. `DASHSCOPE_API_KEY`, `OPENAI_API_KEY`) as fallback. · 也可用供应商专属环境变量兜底。

### Option 2: Manual · 手动指定

| Variable | Required | Description |
|---|---|---|
| `VISION_API_KEY` | Yes · 是 | API key |
| `VISION_BASE_URL` | No · 否 | OpenAI-compatible endpoint · 端点 |
| `VISION_MODEL` | No · 否 | Model name · 模型名 |

Tool params (override env per call): `image`, `prompt`, `image_type`, `provider`, `base_url`, `api_key`, `model`, `temperature`, `max_tokens`.

---

## MCP Client Setup · 客户端注册

### Claude Code (`.mcp.json`)

```json
{
  "mcpServers": {
    "vision": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-vision-server", "mcp-vision-server"],
      "env": {
        "VISION_PROVIDER": "zhipu",
        "VISION_API_KEY": "your_key"
      }
    }
  }
}
```

### Claude Code Plugin · 插件安装

```bash
claude plugins install RuyimgByCN/mcp-vision-server  # after PyPI publish · 发布后
claude plugins install /path/to/mcp-vision-server     # local test · 本地测试
```

### Codex (OpenAI Codex CLI)

Edit `~/.codex/config.toml`: · 编辑 `~/.codex/config.toml`：

```toml
[mcp_servers.vision]
command = "uvx"
args = ["mcp-vision-server"]
env = { VISION_PROVIDER = "zhipu", VISION_API_KEY = "your_key" }
```

Or for local dev: · 本地开发：

```toml
[mcp_servers.vision]
command = "uv"
args = ["run", "--directory", "/path/to/mcp-vision-server", "mcp-vision-server"]
env = { VISION_PROVIDER = "zhipu", VISION_API_KEY = "your_key" }
```

### Cursor / other `uvx` clients · 其它客户端

Replace `command` with `uvx`, `args` with `["--from", "/path/to/mcp-vision-server", "mcp-vision-server"]`, same `env`. · 改 command 为 uvx 即可。

---

## Provider Examples · 切换示例

```json
// Bailian · 阿里百炼
"env": { "VISION_PROVIDER": "bailian", "VISION_API_KEY": "your_key" }

// OpenAI
"env": { "VISION_PROVIDER": "openai", "VISION_API_KEY": "sk-xxx" }

// Fully custom · 完全自定义
"env": {
  "VISION_BASE_URL": "https://your-endpoint/v1",
  "VISION_API_KEY": "your_key",
  "VISION_MODEL": "your-model"
}
```