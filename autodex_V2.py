import json

_save_path = "autodex_data.json"


def _open(path: str) -> list[dict]:
    try:
        with open(path, "r") as file:
            return json.load(file)

    except json.decoder.JSONDecodeError:
        raise Exception(f"Couldn't open {path}")

    except FileNotFoundError:
        raise Exception(f"Couldn't find {path}")

_global_fida = _open(_save_path)

print(_global_fida)
