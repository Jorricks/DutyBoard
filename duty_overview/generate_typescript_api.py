import json
import os
import subprocess
from pathlib import Path

from fastapi.openapi.utils import get_openapi
from server import app

with open("openapi.json", "w") as f:
    openapi_definition = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    json.dump(openapi_definition, f)

cmd = "npx swagger-typescript-api -p ../openapi.json -o ./src -n myApi.ts --axios"
subprocess.run(cmd, cwd=Path.cwd() / "www", shell=True)
os.remove(Path.cwd() / "openapi.json")
