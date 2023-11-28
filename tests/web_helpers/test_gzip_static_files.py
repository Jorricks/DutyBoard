from pathlib import Path
from unittest.mock import patch

from starlette.types import Scope

from duty_board.web_helpers.gzip_static_files import GZIPStaticFiles


def test_gzip_static_files(tmp_path: Path) -> None:
    scope: Scope = {
        "method": "HEAD",
        "headers": [
            (b'host', b'testserver'),
            (b'accept', b'*/*'),
            (b'accept-encoding', b'gzip, deflate'),
            (b'connection', b'keep-alive'),
            (b'user-agent', b'testclient')
        ]
    }

    gzip_server = GZIPStaticFiles(directory=tmp_path, check_dir=False)
    (tmp_path / "main.js").write_bytes("Hallo".encode())

    # This is a standard request.
    result = gzip_server.file_response(
        full_path=tmp_path / "main.js",
        stat_result=(tmp_path / "main.js").stat(),
        scope=scope,
        status_code=200
    )
    assert result.status_code == 200
    assert "content-encoding" not in result.headers
    assert result.headers["content-type"] == "application/javascript"

    # Now we make a request to a file that also has a `.gz` file.
    (tmp_path / "main.js.gz").write_bytes("HalloGZ".encode())
    result = gzip_server.file_response(
        full_path=tmp_path / "main.js",
        stat_result=(tmp_path / "main.js").stat(),
        scope=scope,
        status_code=200
    )
    assert result.status_code == 200
    assert result.headers["content-encoding"] == "gzip"

    # Now we make a request for which we don't have to fetch the most recent file because it has no updated.
    (tmp_path / "main.js.gz").write_bytes("HalloGZ".encode())
    with patch("starlette.staticfiles.StaticFiles.is_not_modified", lambda *_: True):

        result = gzip_server.file_response(
            full_path=tmp_path / "main.js",
            stat_result=(tmp_path / "main.js").stat(),
            scope=scope,
            status_code=200
        )
        assert result.status_code == 304
        assert set(result.headers.keys()) == {"etag"}
