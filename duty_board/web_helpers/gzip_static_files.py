import os
import typing
from pathlib import Path

from starlette.datastructures import Headers
from starlette.responses import FileResponse, Response
from starlette.staticfiles import NotModifiedResponse, StaticFiles
from starlette.types import Scope

PathLike = typing.Union[str, "os.PathLike[str]"]


class GZIPStaticFiles(StaticFiles):
    """90% is inherited and copied from StaticFiles. We just overwrite this method for GZIP compatibility."""

    def file_response(
        self,
        full_path: PathLike,
        stat_result: os.stat_result,
        scope: Scope,
        status_code: int = 200,
    ) -> Response:
        method = scope["method"]
        request_headers = Headers(scope=scope)

        pathlib_path = Path(full_path)
        if (pathlib_path.parent / f"{pathlib_path.name}.gz").exists():
            gzip_headers = {"content-encoding": "gzip"}
            response = FileResponse(
                str(full_path) + ".gz",
                status_code=status_code,
                stat_result=stat_result,
                method=method,
                headers=gzip_headers,
            )
        else:
            response = FileResponse(full_path, status_code=status_code, stat_result=stat_result, method=method)
        if self.is_not_modified(response.headers, request_headers):
            return NotModifiedResponse(response.headers)
        return response
