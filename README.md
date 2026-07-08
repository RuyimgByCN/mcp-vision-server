# mcp-vision-server

[![PyPI](https://img.shields.io/pypi/v/RuyimgBy-mcp-vision-server?label=PyPI&color=blue)](https://pypi.org/project/RuyimgBy-mcp-vision-server/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Personal%20Use%20Only-orange)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-6E29F6)](https://modelcontextprotocol.io/)

One MCP server for every OpenAI-compatible vision model.

Configure once and use the same `analyze_image` tool across OpenAI, DeepSeek, OpenRouter, Zhipu, Bailian, SiliconFlow and other compatible providers. It works with Claude Code, Codex, Cursor, Zed and any other MCP client.

## Why use mcp-vision-server?

- ✅ **Works with any MCP client** – Claude Code, Codex, Cursor, Zed and more.
- ✅ **Works with many providers** – switch providers without changing prompts or tool calls.
- ✅ **One unified API** – one tool (`analyze_image`) for every OpenAI-compatible vision endpoint.
- ✅ **Flexible image input** – URL, local file or Base64 are detected automatically.
- ✅ **Override anywhere** – configure globally with environment variables or per request.

## Quick Start

1. Install the server.
2. Set your provider and API key.
3. Add the MCP server to your client.
4. Ask:

```text
Describe this screenshot.
```

If everything is configured correctly, your MCP client will automatically call `analyze_image` and return the vision model's response.

## Features

- Single `analyze_image` tool with a consistent interface.
- Supports URL, local file and Base64 image inputs.
- Supports 14 built-in provider presets.
- Provider selection via `VISION_PROVIDER` or the `provider` parameter.
- Environment-level and request-level configuration overrides.

## Example

Ask your MCP client to analyze an image:

```text
Analyze this screenshot and tell me what UI is shown.
```

The client calls the MCP tool:

```json
{
  "tool": "analyze_image",
  "arguments": {
    "image": "/path/to/screenshot.png",
    "prompt": "Analyze this screenshot and tell me what UI is shown."
  }
}
```

The server normalizes the image input, sends it to the selected OpenAI-compatible vision provider, and returns a plain text answer to your MCP client.

## Providers

Built-in presets make common OpenAI-compatible vision endpoints easy to use:

| Provider | Preset |
|---|---|
| Zhipu | `zhipu` |
| Bailian / DashScope | `bailian` |
| DeepSeek | `deepseek` |
| OpenAI | `openai` |
| SiliconFlow | `siliconflow` |
| OpenRouter | `openrouter` |
| Ark / Volcengine | `ark` |
| StepFun | `stepfun` |
| Kimi / Moonshot | `kimi` |
| MiniMax | `minimax` |
| ModelScope | `modelscope` |
| NVIDIA NIM | `nvidia` |
| Novita AI | `novita` |

You can also use any other OpenAI-compatible vision endpoint by setting `VISION_BASE_URL`, `VISION_API_KEY`, and `VISION_MODEL` manually.

## Install & Run

Requires Python ≥ 3.10 and [uv](https://docs.astral.sh/uv/).

```bash
cd mcp-vision-server
uv sync                  # install deps
uv run pytest -v         # run tests
uv run ruff check .      # lint
uv run mcp-vision-server # start stdio server
```

## Configuration

### Option 1: Provider preset (recommended)

```bash
export VISION_PROVIDER=zhipu     # default
export VISION_API_KEY=your_key
```

See [Providers](#providers) for the full preset list.

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

## Architecture

```text
MCP Client (Claude Code / Codex / Cursor / Zed)
        │
        ▼
mcp-vision-server
        │
        ├── mcp_vision_server/server.py     # MCP tool entrypoints
        ├── mcp_vision_server/config.py     # env/provider/parameter resolution
        ├── mcp_vision_server/image.py      # URL/file/base64 normalization
        └── mcp_vision_server/providers.py  # provider presets
        │
        ▼
OpenAI-compatible Vision API
        │
        ▼
Vision model response
```

## FAQ

### Why not call the vision provider directly?

This server gives MCP clients a single, reusable vision tool. You can switch providers without changing client prompts, MCP tool names, or client-side integration code.

### Can I use a provider that is not listed?

Yes. Use manual configuration with `VISION_BASE_URL`, `VISION_API_KEY`, and `VISION_MODEL` for any OpenAI-compatible vision endpoint.

### Can I override the provider per request?

Yes. Use the `provider`, `base_url`, `api_key`, or `model` tool parameters to override environment-level configuration for a single call.

### What image formats are supported?

The server accepts image URLs, local file paths, and Base64 strings. Input type can be auto-detected or specified with `image_type`.

## Development

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format .
uv run pytest -v
uv build
uv run twine check dist/*
```

## Release checklist

1. Update the version in `pyproject.toml`.
2. Run `uv run ruff check .`, `uv run pytest -v`, `uv build`, and `uv run twine check dist/*`.
3. Create and push a version tag, for example `v0.1.2`.
4. Let GitHub Actions publish to PyPI through trusted publishing.

## Roadmap

- Add more provider presets when stable OpenAI-compatible vision endpoints are available.
- Add richer examples for Claude Code, Codex, Cursor, and other MCP clients.
- Add optional streaming response support if MCP client UX benefits from it.
- Split provider-specific behavior into plugins only when providers require custom request logic.

## About

**Author:** [RuyimgByCN](https://github.com/RuyimgByCN)

**License:** Personal use only. Commercial use is prohibited — see [LICENSE](LICENSE) for details. Contact the author for commercial licensing.

**中文说明：** 个人使用免费，禁止商用。商业授权请联系作者。详见 [README_ZH.md](README_ZH.md)。
