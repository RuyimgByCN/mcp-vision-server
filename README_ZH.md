# mcp-vision-server

14 个供应商预设的 OpenAI 兼容 vision MCP 服务。

任何 MCP 客户端（Claude Code、Codex、Cursor、ZCode 等）接入后，需要"看图"时自动调用 —— 分析截图、识别内容、读图答题、UI 还原。

## 功能

- 单工具 `analyze_image`：传图片 + 问题，返回文本回复。
- 三种图像输入：**URL** / **本地文件** / **base64 字符串**（自动识别）。
- **14 个供应商预设**：智谱、百炼、DeepSeek、OpenAI、SiliconFlow、OpenRouter、火山方舟、阶跃星辰、Kimi、MiniMax、ModelScope、NVIDIA NIM、Novita AI。
- 通过 `VISION_PROVIDER` 环境变量或 `provider` 参数一键切换供应商。
- 环境变量 + 工具参数两层覆盖。

## 安装与运行

依赖 Python ≥ 3.10、[uv](https://docs.astral.sh/uv/)。

```bash
cd mcp-vision-server
uv sync                  # 安装依赖
uv run pytest -v         # 跑测试（可选）
uv run mcp-vision-server # 启动 stdio server
```

## 配置

### 方式一：供应商预设（推荐）

```bash
export VISION_PROVIDER=zhipu     # 默认
export VISION_API_KEY=你的key
```

支持的 `VISION_PROVIDER` 值：`zhipu` `bailian` `deepseek` `openai` `siliconflow` `openrouter` `ark` `stepfun` `kimi` `minimax` `modelscope` `nvidia` `novita`。

也可用供应商专属环境变量兜底（如 `DASHSCOPE_API_KEY`、`OPENAI_API_KEY`）。

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

仓库自带 [`.claude-plugin.json`](.claude-plugin.json) 清单文件，`claude plugins install` 自动读取。

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