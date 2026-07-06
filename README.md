# mcp-vision-server

把 OpenAI 兼容的 vision 模型暴露为 MCP 工具的 server。
任何支持 MCP 的客户端(ZCode、Claude Code、Cursor 等)接入后,在需要"看图"
——分析截图、识别内容、读图答题、UI 还原——时会自动调用它。

## 功能

- 单工具 `analyze_image`:传图像 + 问题,返回模型的文本回复。
- 图像输入三选一:**URL** / **本地文件路径** / **base64 字符串**(可自动识别)。
- **14 个供应商预设**:智谱、百炼、DeepSeek、OpenAI、SiliconFlow、OpenRouter、火山方舟、阶跃星辰、Kimi、MiniMax、ModelScope、NVIDIA NIM、Novita AI。
- 通过 `VISION_PROVIDER` 环境变量或 `provider` 参数一键切换供应商。
- 配置可在 **环境变量** 与 **工具调用参数** 两层覆盖。

## 安装与运行

依赖 Python ≥ 3.10、[uv](https://docs.astral.sh/uv/)。

```bash
cd mcp-vision-server
uv sync                 # 安装依赖
uv run pytest -v        # 跑测试(可选)
uv run mcp-vision-server  # 启动 stdio server(会挂起等待 MCP 客户端)
```

## 配置

### 方式一:供应商预设(推荐)

```bash
export VISION_PROVIDER=bailian   # 切换到阿里百炼
export VISION_API_KEY=你的key
```

支持的 `VISION_PROVIDER` 值:`zhipu`(默认)、`bailian`、`deepseek`、`openai`、`siliconflow`、`openrouter`、`ark`、`stepfun`、`kimi`、`minimax`、`modelscope`、`nvidia`、`novita`。

也可用供应商专属环境变量代替 `VISION_API_KEY`(如 `DASHSCOPE_API_KEY`、`OPENAI_API_KEY`)。

### 方式二:手动指定

| 变量 | 必填 | 说明 |
|---|---|---|
| `VISION_API_KEY` | 是 | API key |
| `VISION_BASE_URL` | 否 | OpenAI 兼容端点 |
| `VISION_MODEL` | 否 | 模型名 |

工具参数(每次调用可覆盖,优先级高于环境变量):`image`、`prompt`、`image_type`、`provider`、`base_url`、`api_key`、`model`、`temperature`、`max_tokens`。

## 在 MCP 客户端中注册

### ZCode / Claude Code(项目级 `.mcp.json`)

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

### Cursor / 其它走 `uvx` 的客户端

改 `command` 为 `uvx`,`args` 改成 `["--from", "/绝对路径/mcp-vision-server", "mcp-vision-server"]`,`env` 同上。

### Claude Code 插件安装

```bash
# PyPI 发布后
claude plugins install RuyimgByCN/mcp-vision-server

# 或本地测试
claude plugins install /path/to/mcp-vision-server
```

### Codex (OpenAI Codex CLI)

编辑 `~/.codex/config.toml`，添加 `[mcp_servers.vision]` 段:

```toml
[mcp_servers.vision]
command = "uvx"
args = ["mcp-vision-server"]
env = { VISION_PROVIDER = "zhipu", VISION_API_KEY = "your_key" }
```

本地开发时也可用 `uv run`:

```toml
[mcp_servers.vision]
command = "uv"
args = ["run", "--directory", "/绝对路径/mcp-vision-server", "mcp-vision-server"]
env = { VISION_PROVIDER = "zhipu", VISION_API_KEY = "your_key" }
```

## 切换供应商示例

```json
// 阿里百炼
"env": {
  "VISION_PROVIDER": "bailian",
  "VISION_API_KEY": "你的百炼key"
}

// OpenAI
"env": {
  "VISION_PROVIDER": "openai",
  "VISION_API_KEY": "sk-xxx"
}

// 完全自定义
"env": {
  "VISION_BASE_URL": "https://your-endpoint/v1",
  "VISION_API_KEY": "your_key",
  "VISION_MODEL": "your-model"
}
```