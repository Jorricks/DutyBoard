import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict

from fastapi.openapi.utils import get_openapi

from duty_board.server import app


def to_camel_case(snake_str: str) -> str:
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x[0].upper() + x[1:] for x in components[1:])


def convert_dict_from_snake_to_camel(given_value: Any) -> Any:
    if isinstance(given_value, (bool, int, float)):
        return given_value
    if isinstance(given_value, list):
        return [
            to_camel_case(item) if isinstance(item, str) else convert_dict_from_snake_to_camel(item)
            for item in given_value
        ]
    if isinstance(given_value, dict):
        return {
            to_camel_case(key): to_camel_case(value)
            if isinstance(value, str)
            else convert_dict_from_snake_to_camel(value)
            for key, value in given_value.items()
        }
    raise ValueError(f"Unexpected value {given_value=}.")


with open("openapi.json", "w") as f:
    openapi_definition: Dict[str, Any] = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    import pprint

    pprint.pprint(openapi_definition)
    openapi_camel_case = convert_dict_from_snake_to_camel(openapi_definition)
    json.dump(openapi_camel_case, f)

# consider removing --axios and adding --no-client.
output_folder = "./js/api"
output_file = "api-generated-types.ts"
cmd = f"npx swagger-typescript-api -p ../web_helpers/openapi.json -o {output_folder} -n {output_file} --no-client"
subprocess.run(cmd, cwd=Path.cwd().parent / "www", shell=True)
os.remove(Path.cwd() / "openapi.json")
