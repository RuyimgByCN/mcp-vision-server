"""Runtime configuration resolution for the vision MCP server."""

from __future__ import annotations

import os

from mcp_vision_server.providers import DEFAULT_PROVIDER, PROVIDERS


def resolve_config(
    provider: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> tuple[str | None, str | None, str | None]:
    """Resolve effective ``base_url``/``api_key``/``model``.

    Priority: explicit parameters > environment variables > provider defaults.
    """
    provider_key = provider or os.environ.get("VISION_PROVIDER") or DEFAULT_PROVIDER
    preset = PROVIDERS.get(provider_key, {})

    base_url = (
        base_url or os.environ.get("VISION_BASE_URL") or preset.get("base_url", "")
    )
    api_key = (
        api_key
        or os.environ.get("VISION_API_KEY")
        or os.environ.get(preset.get("api_key_env", ""))
    )
    model = model or os.environ.get("VISION_MODEL") or preset.get("model", "")
    return base_url or None, api_key or None, model or None
