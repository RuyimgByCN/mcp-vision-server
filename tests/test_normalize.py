import base64
import os
import tempfile

from mcp_vision_server.image import normalize_image


def test_url_returned_as_is():
    assert normalize_image("https://example.com/a.png") == "https://example.com/a.png"
    assert normalize_image("http://foo.bar/img.jpg") == "http://foo.bar/img.jpg"
    assert (
        normalize_image("data:image/png;base64,ABC123")
        == "data:image/png;base64,ABC123"
    )


def test_explicit_file_missing_returns_error():
    result = normalize_image("/tmp/not-existing-image.png", image_type="file")
    assert result.startswith("[错误] 文件不存在:")


def test_explicit_base64_short_value_gets_prefix():
    assert (
        normalize_image("ABC123", image_type="base64") == "data:image/png;base64,ABC123"
    )


def test_explicit_url_returns_string_without_validation():
    assert normalize_image("not really a url", image_type="url") == "not really a url"


def test_local_file_becomes_data_uri():
    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91Jpz"
        "AAAAC0lEQVR42mNk+M9QDwADhgGAWjF9cAAAAABJRU5ErkJggg=="
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as file_obj:
        file_obj.write(png_bytes)
        path = file_obj.name
    try:
        result = normalize_image(path)
        assert result.startswith("data:image/png;base64,")
        encoded = result.split(",", 1)[1]
        assert base64.b64decode(encoded) == png_bytes
    finally:
        os.unlink(path)


def test_bare_base64_gets_prefix():
    b64 = "A" * 100
    result = normalize_image(b64)
    assert result == f"data:image/png;base64,{b64}"


def test_unrecognized_returns_error_string():
    result = normalize_image("not a url / not a path / and has spaces!!")
    assert isinstance(result, str)
    assert result.startswith("[错误]")
