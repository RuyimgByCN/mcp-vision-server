"""Image input normalization utilities."""

from __future__ import annotations

import base64
import mimetypes
import os
import re

# Bare base64 legal chars + minimum length to avoid matching ordinary short text.
_B64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
_B64_MIN_LEN = 64


def normalize_image(image: str, image_type: str = "auto") -> str:
    """Normalize image input into an OpenAI vision ``image_url.url`` value.

    - URL -> returned as-is
    - local file path -> encoded as ``data:<mime>;base64,<...>``
    - bare base64 -> prefixed with ``data:image/png;base64,``
    - unrecognized input -> returns a human-readable ``[错误]`` string

    ``image_type`` can be explicitly set to ``url``/``file``/``base64`` to skip
    auto-detection.
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

    if img.startswith(("http://", "https://", "data:")):
        return _as_url()
    if os.path.exists(img):
        return _as_file()
    if len(img) >= _B64_MIN_LEN and _B64_RE.match(img):
        return _as_base64()
    return (
        "[错误] 无法自动识别 image 类型。"
        "请显式传 image_type 为 'url' / 'file' / 'base64'。"
    )
