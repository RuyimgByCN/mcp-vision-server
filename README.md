# mcp-vision-server

OpenAI-compatible vision MCP server with 14 provider presets.

Any MCP client (Claude Code, Codex, Cursor, ZCode…) can call it to "see" images — analyze screenshots, recognize content, read text, answer visual questions, restore UI from mockups.

## Features

- Single tool `analyze_image`: pass an image + prompt, get text response.
- Three image input types: **URL** / **local file** / **base64 string** (auto-detect).
- **14 provider presets**: Zhipu, Bailian, DeepSeek, OpenAI, SiliconFlow, OpenRouter, Ark, StepFun, Kimi, MiniMax, ModelScope, NVIDIA NIM, Novita AI.
- Switch providers via `VISION_PROVIDER` env var or `provider` parameter.
- Override at both **env** and **tool parameter** levels.

## Install & Run

Requires Python ≥ 3.10 and [uv](https://docs.astral.sh/uv/).

```bash
cd mcp-vision-server
uv sync                  # install deps
uv run pytest -v         # run tests (optional)
uv run mcp-vision-server # start stdio server
```

## Configuration

### Option 1: Provider preset (recommended)

```bash
export VISION_PROVIDER=zhipu     # default
export VISION_API_KEY=your_key
```

Supported presets: `zhipu` `bailian` `deepseek` `openai` `siliconflow` `openrouter` `ark` `stepfun` `kimi` `minimax` `modelscope` `nvidia` `novita`.

You can also use provider-specific env vars (e.g. `DASHSCOPE_API_KEY`, `OPENAI_API_KEY`) as fallback.

### Option 2: Manual

| Variable | Required | Description |
|---|---|---|
| `VISION_API_KEY` | Yes | API key |
| `VISION_BASE_URL` | No | OpenAI-compatible endpoint |
| `VISION_MODEL` | No | Model name |

Tool params (override env per call): `image`, `prompt`, `image_type`, `provider`, `base_url`, `api_key`, `model`, `temperature`, `max_tokens`.

## MCP Client Setup

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

### Claude Code Plugin

```bash
# After PyPI publish
claude plugins install RuyimgByCN/mcp-vision-server

# Local test
claude plugins install /path/to/mcp-vision-server
```

The repo includes a [`.claude-plugin.json`](.claude-plugin.json) manifest — `claude plugins install` reads it automatically.

### Codex (OpenAI Codex CLI)

Edit `~/.codex/config.toml`:

```toml
[mcp_servers.vision]
command = "uvx"
args = ["mcp-vision-server"]
env = { VISION_PROVIDER = "zhipu", VISION_API_KEY = "your_key" }
```

Or for local dev:

```toml
[mcp_servers.vision]
command = "uv"
args = ["run", "--directory", "/path/to/mcp-vision-server", "mcp-vision-server"]
env = { VISION_PROVIDER = "zhipu", VISION_API_KEY = "your_key" }
```

### Cursor / other `uvx` clients

Replace `command` with `uvx`, `args` with `["--from", "/path/to/mcp-vision-server", "mcp-vision-server"]`, same `env`.

## Provider Examples

```json
// Bailian
"env": { "VISION_PROVIDER": "bailian", "VISION_API_KEY": "your_key" }

// OpenAI
"env": { "VISION_PROVIDER": "openai", "VISION_API_KEY": "sk-xxx" }

// Fully custom
"env": {
  "VISION_BASE_URL": "https://your-endpoint/v1",
  "VISION_API_KEY": "your_key",
  "VISION_MODEL": "your-model"
}
```