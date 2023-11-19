import json
import pprint
import subprocess
from pathlib import Path
from typing import Any, Dict

import requests


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


def write_to_openapi(path_to_openapi: Path) -> None:
    with path_to_openapi.open("w") as f:
        result = requests.get("http://127.0.0.1:8000/openapi.json", timeout=5)
        openapi_definition: Dict[str, Any] = result.json()
        pprint.pprint(openapi_definition)
        openapi_camel_case = convert_dict_from_snake_to_camel(openapi_definition)
        json.dump(openapi_camel_case, f)


def generate_typescript_client() -> None:
    output_folder = "./js/api"
    output_file = "api-generated-types.ts"
    cmd = f"npx swagger-typescript-api -p openapi.json -o {output_folder} -n {output_file} --no-client"
    docker_run_cmd = f'docker exec duty_frontend /bin/bash -c "{cmd}"'
    subprocess.run(docker_run_cmd, cwd=Path.cwd().parent / "www", shell=True, check=True)  # noqa: S602


def run() -> None:
    path_to_openapi = Path.cwd().parent / "www" / "openapi.json"
    write_to_openapi(path_to_openapi)
    print(f"Written openapi.json to {path_to_openapi!s}.")
    generate_typescript_client()
    path_to_openapi.unlink()
    print("Removed openapi.json again.")


if __name__ == "__main__":
    run()
