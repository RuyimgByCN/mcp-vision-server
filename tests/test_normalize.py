import base64
import os
import tempfile

from mcp_vision_server.server import normalize_image


def test_url_returned_as_is():
    """http(s) URL 和 data: URI 直接返回原字符串。"""
    assert normalize_image("https://example.com/a.png") == "https://example.com/a.png"
    assert normalize_image("http://foo.bar/img.jpg") == "http://foo.bar/img.jpg"
    assert normalize_image("data:image/png;base64,ABC123") == "data:image/png;base64,ABC123"


def test_local_file_becomes_data_uri():
    """存在的本地文件 → 读取并编码为 data URI。"""
    # 准备一个临时 PNG(2x2 像素的最小 PNG 字节)
    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAC0lEQVR42mNk+M9QDwADhgGAWjF9cAAAAABJRU5ErkJggg=="
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(png_bytes)
        path = f.name
    try:
        result = normalize_image(path)
        assert result.startswith("data:image/png;base64,")
        # data URI 的 base64 部分解码后应等于原文件字节
        encoded = result.split(",", 1)[1]
        assert base64.b64decode(encoded) == png_bytes
    finally:
        os.unlink(path)


def test_bare_base64_gets_prefix():
    """裸 base64 字符串补默认 data URI 前缀。"""
    # 长度 ≥ 64 且只含合法字符
    b64 = "A" * 100
    result = normalize_image(b64)
    assert result == f"data:image/png;base64,{b64}"


def test_unrecognized_returns_error_string():
    """无法识别(非 URL、非文件、非 base64)→ 返回错误字符串。"""
    result = normalize_image("not a url / not a path / and has spaces!!")
    assert isinstance(result, str)
    assert result.startswith("[错误]")
