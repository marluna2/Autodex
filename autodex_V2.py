import json
from pathlib import Path

save_path = "autodex_data.json"

template_soda = {
    "Cusoco": int,
    "Storage unit": str,
    "Container type": str,
    "Location": dict,
    "Name": str,
    "Description": str,
    "Contents": list,
    "Tags": list,
    "Numeric attributes": dict,
    "Categorical attributes": dict,
    "Image paths": list,
    "F3D folder path": str
}

storage_units = dict()
container_types = dict()
date_format = str()
global_fida = list()


def read() -> list[dict]:
    global global_fida

    return global_fida.copy()


def write(fida: list[dict]) -> None:
    global global_fida

    global_fida = fida.copy()


def standalone_check(soda: dict) -> [None, str]:
    """Check if a soda is valid, without taking stored sodas into consideration"""

    if soda.keys() != template_soda.keys():
        return ("Soda",
                "Invalid key(s)")

    for key, value in soda.items():
        if type(value) is not template_soda[key]:
            return (key,
                    "Invalid value type(s)", key, value)

    soda_name = soda["Name"]
    if not soda_name.strip():
        return ("Name",
                "Invalid name", soda_name)

    soda_cusoco = soda["Cusoco"]
    if soda_cusoco < 1:
        return ("Cusoco",
                "Invalid cusoco", soda_cusoco)

    soda_storage_unit = soda["Storage unit"]
    if soda_storage_unit not in storage_units.keys():
        return ("Storage unit",
                "Invalid storage unit", soda_storage_unit)

    soda_container_type = soda["Container type"]
    if soda_container_type not in container_types.keys():
        return ("Container type",
                "Invalid container type", soda_container_type)

    if soda_storage_unit not in container_types[soda_container_type].keys():
        return ("Storage unit",
                "Container type not compatible with storage unit", soda_storage_unit, soda_storage_unit)

    for key in ("Contents", "Tags", "Image paths"):

        seen = []
        soda_key = soda[key]
        for i in soda_key:

            if type(i) is not str:
                return (key,
                        "Non-string item(s) found in list", key, soda_key)

            if i in seen:
                return (key,
                        "Duplicate items in list", key, soda_key, i)

            if not i.strip():
                return (key,
                        "Empty item(s) in list", key, soda_key)

            seen.append(i)

    for key, value in soda["Numeric attributes"].items():

        if type(value) is not dict:
            return ("Numeric attributes",
                    "Numeric attribute unit/value group(s) not in dicts(s)", key, value)

        for i in value.values():
            if type(i) is not list:
                return ("Numeric attributes",
                        "Numeric attribute value(s) not in list(s)", key, value)

            if not i:
                return ("Numeric attributes",
                        "Numeric attribute list empty", key, value, j)

            seen = []
            for j in i:
                if type(j) not in (int, float):
                    return ("Numeric attributes",
                            "Numeric attribute value type(s) not int(s) or float(s)", key, value, j)

                if not j:
                    return ("Numeric attributes",
                            "Numeric attribute value(s) empty", key, value, j)

                if j in seen:
                    return ("Numeric attributes",
                            "Numeric attribute value(s) duplicate", key, value, j)

                seen.append(j)

    for key, value in soda["Categorical attributes"].items():

        if type(value) is not list:
            return ("Categorical attributes",
                    "Categorical attribute value(s) not in list(s)", key, value)

        seen = []
        for i in value:

            if type(i) is not str:
                return ("Categorical attributes",
                        "Categorical attribute value type(s) not string(s)", key, value, i)

            if not i.strip():
                return ("Categorical attributes",
                        "Categorical attribute value(s) empty", key, value, i)

            if i in seen:
                return ("Categorical attributes",
                        "Categorical attribute value(s) duplicate", key, value, i)

            seen.append(i)

    for i in soda["Image paths"]:
        if not Path(i).exists():
            return ("Image paths",
                    "Image path not found", i)

        if not i.endswith((".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff", ".webp", ".bmp", ".svg")):
            return ("Image paths",
                    "Image path doesn't lead to an image type file", i)

    soda_f3d_folder_path = soda["F3D folder path"]
    if soda_f3d_folder_path:

        path = Path(soda_f3d_folder_path)

        if not path.exists():
            return ("F3D folder path",
                    "F3D folder path not found", str(path.absolute()))

        if not path.is_dir():
            return ("F3D folder path",
                    "F3D folder path isn't a directory", str(path.absolute()))

        for i in path.iterdir():
            if not i.is_dir():
                return ("F3D folder path",
                        "F3D folder contains files", str(i), str(path.absolute()))

        for i in path.iterdir():
            for j in i.iterdir():

                if j.is_dir():
                    return ("F3D folder path",
                            "F3D image group contains folders", str(path.absolute()))

                if not str(j).endswith((".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff", ".webp", ".bmp", ".svg")):
                    return ("F3D folder path",
                            "F3D contains non-image type file", str(j), str(path.absolute()))

    limits = storage_units[soda_storage_unit]
    size = container_types[soda_container_type][soda_storage_unit]
    location = soda["Location"]

    if limits.keys() != location.keys():
        return ("Location",
                "Invalid location keys", location)

    location_plus_size = location.copy()

    for key, value in size.items():
        location_plus_size[key] += value - 1

    for key, value in location.items():
        key_limits = limits[key]
        if value < key_limits[0] or value > key_limits[1]:
            return ("Location",
                    "Base location out of bounds", key, value, key_limits)

    for key, value in location_plus_size.items():
        key_limits = limits[key]
        if value < key_limits[0] or value > key_limits[1]:
            return ("Location",
                    "Location combined with container size out of bounds", key, value, key_limits)


def collective_check(soda: dict) -> [None, str]:
    """Check if a soda is valid, and if it doesn't have matching values of existing sodas"""

    standalone_return = standalone_check(soda)
    if standalone_return:
        return standalone_return

    for i in read():
        for key in ("Cusoco", "Name"):
            if i[key] == soda[key]:
                return (key,
                        "Duplicate value(s)", key, soda[key])

        i_storage_unit = i["Storage unit"]
        soda_storage_unit = soda["Storage unit"]

        if i_storage_unit == soda_storage_unit:
            a = soda["Location"]
            b = i["Location"]

            size_a = container_types[soda["Container type"]][soda_storage_unit]
            size_b = container_types[i["Container type"]][i_storage_unit]

            a_plus_size = a.copy()
            b_plus_size = b.copy()

            for key, value in size_a.items():
                a_plus_size[key] += value - 1

            for key, value in size_b.items():
                b_plus_size[key] += value - 1

            overlapping = True
            for key, a_key_value in a.items():
                b_key_value = b[key]

                a_key_plus_size = a_plus_size[key]
                b_key_plus_size = b_plus_size[key]

                if not (a_key_value <= b_key_plus_size and a_key_plus_size >= b_key_value):
                    overlapping = False
                    break
        else:
            overlapping = False

        if overlapping:
            return ("Location",
                    "Container location is overlapping another container's location", {"Cusoco": i["Cusoco"]}, a, b)


def add(soda: dict) -> None:
    collective_return = collective_check(soda)
    if collective_return:
        return collective_return


# Load file
try:
    with open(save_path, "r") as file:
        data = json.load(file)

        print("Running Autodex:", data[0]["Autodex version"], "    Last saved:", data[0]["Last saved"])
        storage_units = data[0]["Storage units"]
        container_types = data[0]["Container types"]
        date_format = data[0]["Date format"]

        if len(data) > 1:
            global_fida = data[1:]
        else:
            global_fida = []
except json.decoder.JSONDecodeError:
    raise Exception(f"Can't read {save_path}")
except FileNotFoundError:
    raise Exception(f"Can't find {save_path}")

add({
    "Cusoco": 2,
    "Storage unit": "Small shelf",
    "Container type": "Greiner small",
    "Location": {"Floor": 2, "X": 1, "Y": 4, "Z": 2},
    "Name": "Test box 2",
    "Description": "Hello world!",
    "Contents": ["Item a", "Item b", "Item c"],
    "Tags": ["Valve", "Pneumatic", "Electromagnetic", "Electric", "Electromechanical", "Mechanical"],
    "Numeric attributes": {"Pressure": {"bar": [6.3, 8]}, "Voltage": {"Vdc": [6, 12], "Vac": [1]}},
    "Categorical attributes": {"Manufacturer": ["Rexroth", "SMC", "Festo"], "Valve type": ["3/2 Way", "5/2 Way"]},
    "Image paths": [],
    "F3D folder path": ""
})
