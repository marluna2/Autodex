"""
Responsible for storing, changing and retrieving data about containers and their contents.

cusoco - The custom sorting code, is assigned to each and every container and must only exist once.
It is the only identifier about a container, as all the other information is stored in a .json file.

soda - The sorting data, is the full dictionary with cusoco, date of creation, name, ect. of a container.

fida - The file data, is the complete data from the autodex_data.json file, consisting of dictionaries in a list.

Common arguments:
cusoco: An individual id given to every container, irrespective of type or location.\n
storage_unit: In which piece of furniture the container is stored, can also be "parent".\n
location: Where in that storage unit it's located, or parent id: section 5 depth 2 x-axis 6/container #456.\n
name: A general description of its contents: screws/small switches.\n
image_paths: File paths from images of its contents.\n
contents: List of the containers contents incl. children: m4 screws/container #123.\n
description: Simple description of where contents may stem from, or use cases: dryer/pump.\n

A complete soda looks like this: {
"cusoco": 2,
"storage_unit": "small_shelf_even",
"container_type": "greiner_small",
"location": {
"floor": 2,
"x": 1,
"y": 1,
"z": 1
},
"name": "test 1",
"description": "",
"image_paths": [],
"contents": [],
"date_created": "2025-01-16T23:00:12.978108Z",
"date_changed": "2025-01-16T23:00:40.654869Z"
    }
"""
import json
import math
import os.path
import itertools
import shutil
import time
from datetime import datetime
from operator import itemgetter
from typing import Literal, List

_data_path = "autodex_data.json"
_container_types = {"A box": {"Some storage unit": {"Y": 2}},
                    "Another box": {"Some storage unit": {"Y": 3}, "Another storage unit": {}}}
_storage_units = {
    "Some storage unit":
        {
            "Floor": range(1, 8),
            "X": range(1, 9),
            "Y": range(1, 8),
            "Z": range(1, 3)
        },
    "Another storage unit":
        {"foo": range(1, 5)}
}

_template_soda = {
    "cusoco": "Preset",
    "storage_unit": "Preset",
    "container_type": "Preset",
    "location": "Preset",
    "name": None,
    "description": None,
    "image_paths": "Preset",
    "contents": "Preset",
    "date_created": "Preset",
    "date_changed": "Preset"
}
_date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
_global_fida = []


def _pre_code_fida_integrity_checks():
    if not _data_path.endswith(".json"):
        raise Exception("File type has to be .json.")
    elif not os.path.isfile(_data_path):
        raise Exception("File not found.")
    elif not json.load(open(_data_path, "r")):
        raise Exception("Warning: File may or may not be corrupted. "
                        f"To continue once anyway, replace the file's contents with "
                        f"[\"corruption safety override\"]")
    elif json.load(open(_data_path, "r")) == [{}]:
        raise Exception("File may be corrupted.")

    if (json.load(open(_data_path, "r")) ==
            ["corruption safety override"]):  # If the corruption safety has been overridden,
        with open(_data_path, "w") as file:
            json.dump([], file, indent=4)  # clear the file of the override key the file and continue.

        print(f"{5 * '#'} Corruption safety has been overridden, executing code. {5 * '#'}")


_pre_code_fida_integrity_checks()
try:
    with open(_data_path, "r") as _fida:
        _global_fida = json.load(_fida)
except json.decoder.JSONDecodeError:  # If the file can't be read, error out.
    raise Exception(f"File {_data_path} corrupted.")


def _read() -> List[dict]:
    global _global_fida

    return _global_fida.copy()


def _write(fida) -> None:
    global _global_fida

    _global_fida = fida.copy()


def _find(search_soda: dict) -> list:
    """
    Find all sodas that have all their key-value-pairs match those of the search_soda.
    :return: A list of the indexes from the found sodas.
    """

    search_soda_copy = search_soda.copy()

    fida = _read()

    found_indexes = []

    for i in range(len(fida)):
        soda = fida[i]  # Iterate through all sodas.

        if all(item in soda.items() for item in search_soda_copy.items()):  # If search_soda fits into current soda,
            found_indexes.append(i)  # append the current soda's index to a list.

    return found_indexes


def get(search_soda: dict, partial_coords: bool = False, fida: List[dict] = None) -> List[dict]:
    """
    Get all sodas that have all their key-value-pairs match those of the search_soda.
    :param partial_coords: If enabled, all of these: [1, 2], 4, [3], [1, 2, 3, 4, 5] would match [2, 3, 4].
        Else only [2, 3, 4] would match [2, 3, 4].
    :return: A list of the found sodas.
    """

    if fida is None:
        fida_copy = _read()
    else:
        fida_copy = fida.copy()

    search_soda_copy = search_soda.copy()

    found_sodas = []

    for soda in fida_copy:
        try:
            correct = True
            for item in search_soda_copy.items():
                if item[0] == "location":

                    for coord in item[1].items():
                        if partial_coords:
                            a = (item[1][coord[0]])
                            b = (soda["location"][coord[0]])

                            if isinstance(a, int):
                                a = [a]
                            if isinstance(b, int):
                                b = [b]

                            # Check for intersection using sets
                            if not (bool(set(a) & set(b))):
                                correct = False

                        else:
                            if item[1][coord[0]] != soda["location"][coord[0]]:
                                correct = False

                elif item[1] != soda[item[0]]:
                    correct = False

            if correct:
                found_sodas.append(soda)

        except KeyError:
            pass

    return found_sodas


def exists(search_soda, partial_coords: bool = False, fida: List[dict] = None) -> bool:
    """
    Return True if at least one soda has all its key-value-pairs match those of the search_soda.
    :param partial_coords: If enabled, all of these: [1, 2], 4, [3], [1, 2, 3, 4, 5] would match [2, 3, 4].
        Else only [2, 3, 4] would match [2, 3, 4].
    """

    return bool(get(search_soda=search_soda, partial_coords=partial_coords, fida=fida))


def _replace(search_soda: dict, replacement_soda: dict, replace_all: bool = True) -> None:
    """
    Replace one or more sodas that have all their key-value-pairs match those of the search_soda
    with the replacement_soda.
    :param replace_all: If all sodas instead of just one soda should be replaced, if multiple sodas are found.
    """

    search_soda_copy = search_soda.copy()
    replacement_soda_copy = replacement_soda.copy()

    primary_fida = _read()
    secondary_fida = primary_fida.copy()

    for i in range(len(secondary_fida)):
        soda = secondary_fida[i]  # Iterate through all sodas.

        if all(item in soda.items() for item in search_soda_copy.items()):  # If search_soda fits into current soda,
            primary_fida[i] = replacement_soda_copy  # replace that current soda with the replacement_soda.

            if not replace_all:
                break

    _check_fida(primary_fida)

    _write(primary_fida)


def check_soda(soda: dict, incomplete_soda: bool = False) -> None:
    """
    Check compliance of the soda with the soda guidelines.
    Returns only if the soda is valid.
    :param soda: The dictionary to be checked.
    :param incomplete_soda: True if the soda doesn't have all the required keys on purpose.
    """

    soda_copy = soda.copy()

    _container_types_copy = _container_types.copy()

    if incomplete_soda and not len(soda_copy):
        raise Exception("Soda is empty.")

    if not incomplete_soda:  # Check if all required keys are present.
        for key in _template_soda:
            if key not in soda_copy:
                raise Exception(f"check_soda: Key \"{key}\" is missing.")

    # The checks being performed:
    # <editor-fold desc="cusoco">
    if not incomplete_soda or "cusoco" in soda_copy:

        cusoco = soda_copy["cusoco"]

        if type(cusoco) is not int or cusoco < 1:
            raise Exception(f"cusoco: #{cusoco} isn't an integer.")
    # </editor-fold>
    # <editor-fold desc="storage_unit and location">
    if not incomplete_soda or "storage_unit" in soda_copy or "location" in soda_copy:

        storage_unit = soda_copy["storage_unit"]
        location = soda_copy["location"]

        if storage_unit != "parent" or location.keys() != ["cusoco"] or not exists({"cusoco": location["cusoco"]}):

            if storage_unit not in _storage_units:  # Check that the storage unit is valid.
                raise Exception("storage_unit and location: Storage unit doesn't exist.")

            locations_required = _storage_units[storage_unit]  # Get dict with valid value ranges for the storage unit.

            if len(locations_required) != len(
                    location):  # Check that the amount of arguments given and required are the same.
                raise Exception("storage_unit and location: Invalid amount of arguments.")

            for key in location:  # Iterate through each key.

                value = location[key]  # Get the value of the current key.

                if type(value) is not list:
                    value = [value]

                for single_value in value:
                    if key in locations_required:  # Check that the current key is in the list of required keys.

                        if locations_required[key] == math.inf and single_value:  # Check if the value is infinity,
                            pass  # as that can't be checked using range().

                        elif single_value not in locations_required[key]:  # Check that it's inside its allowed range.
                            raise Exception(f"storage_unit and location: {key}: {single_value} "
                                            f"doesn't meet its requirements.")

                    else:
                        raise Exception(f"storage_unit and location: The key {key} isn't in the requirements.")
    # </editor-fold>
    # <editor-fold desc="container_type">
    if (not incomplete_soda or
            "container_type" in soda_copy):

        container_type = soda_copy["container_type"]

        if (container_type != "bag" or
                storage_unit != "parent" or
                not exists({"cusoco": location["cusoco"]}) or
                len(location) != 1):

            if container_type not in _container_types_copy:
                raise Exception(f"container_type: The container type \"{container_type}\" doesn't exist.")

            elif storage_unit not in list(_container_types_copy[container_type].keys()):
                raise Exception(f"container_type: Storage unit \"{storage_unit}\" "
                                f"doesn't allow the container type \"{container_type}\".")
    # </editor-fold>
    # <editor-fold desc="location_size_ranges">
    if (not incomplete_soda or
            ("storage_unit" in soda_copy and "location" in soda_copy and "container_type" in soda_copy)):

        sizes = _container_types_copy[container_type][storage_unit]

        for i in list(_storage_units[storage_unit].keys()):

            if i not in sizes:
                sizes.update({i: 1})

        for axis in soda_copy["location"].keys():
            if axis in _container_types_copy[container_type][storage_unit]:

                values = soda_copy["location"][axis]
                if type(values) is not list:
                    values = [values]

                specific_value_range = range(list(set(values))[0], sizes[axis] + list(set(values))[0])

                for i in range(max(len(values), len(specific_value_range))):
                    if 0 <= i < len(values):
                        if values[i] not in specific_value_range:
                            raise Exception(
                                f"location_size_ranges: {axis}: {values[i]} "
                                f"doesn't fit into range: {list(specific_value_range)}.")

                    else:
                        raise Exception(
                            f"location_size_ranges: {axis}: {values[i]} "
                            f"doesn't fit into range: {list(specific_value_range)}.")
    # </editor-fold>
    # <editor-fold desc="name">
    if not incomplete_soda or "name" in soda_copy:

        name = soda_copy["name"]

        if type(name) is not str or name.strip() == "":
            raise Exception(f"name: The name \"{name}\" isn't a string or is empty.")
    # </editor-fold>
    # <editor-fold desc="description">
    if not incomplete_soda or "description" in soda_copy:

        description = soda_copy["description"]

        if type(description) is not str:
            raise Exception(f"description: The description \"{description}\" isn't a string.")
    # </editor-fold>
    # <editor-fold desc="image_paths">
    if not incomplete_soda or "image_paths" in soda_copy:

        image_paths = soda_copy["image_paths"]

        if type(image_paths) is not list:
            raise Exception(f"image_paths: Image paths have to be in a list.")

        for path in image_paths:
            if not os.path.isfile(path) and type(path) is not None:
                raise Exception(f"image_paths: The image path \"{path}\" doesn't lead to a file.")
    # </editor-fold>
    # <editor-fold desc="contents">
    if not incomplete_soda or "contents" in soda_copy:

        contents = soda_copy["contents"]

        if type(contents) is not list:
            raise Exception(f"contents: The contents have to be in a list.")

        if contents:
            for content in contents:

                if type(content) is int:
                    if not exists({"cusoco": content}):
                        raise Exception(f"contents: No container #{content} exists.")

                    elif not get({"cusoco": content})[0] == {"storage_unit": "parent", "location": content}:
                        raise Exception(f"contents: The parent container #{content} "
                                        f"isn't a child container of container #{cusoco}.")

                elif type(content) is not str or not content.strip():
                    raise Exception(f"contents: The content \"{content}\" isn't a string or #.")
    # </editor-fold>
    # <editor-fold desc="date_created and date_changed">
    if not incomplete_soda or "date_created" in soda_copy or "date_changed" in soda_copy:

        for date in ("date_created", "date_changed"):
            if date == "date_changed" and soda_copy[date] is None:  # date_changed can be None, date_created mustn't.
                break

            try:
                date = datetime.strptime(soda_copy[date], _date_format)  # Turn string into a datetime.
            except ValueError:  # If the string could not be turned into a datetime, return false.
                raise Exception(
                    f"date_created and date_changed: \"{date}\": \"{soda_copy[date]}\" "
                    f"isn't a valid datetime.")

            age = (date
                   - datetime.strptime("2025-01-04T00:00:00.0Z", _date_format)  # When this was written.
                   ).total_seconds()  # Calculate datetime difference in seconds.

            difference = (datetime.now()
                          - date
                          ).total_seconds()  # Calculate how long ago the datetime was in seconds.

            age = age / 31556952  # Turn seconds into years with 365.2425 * 24 * 60 * 60.
            difference = difference / 31556952 + 0.01  # + 0.01 accounts for the datetime being set before this ran.

            if (difference < 0  # Check that the date isn't significantly in the future,
                    or age < 0):  # and that it doesn't occur before the original writing of this code.
                raise Exception(f"date_created and date_changed: "
                                f"The date \"{date}\": \"{soda_copy[date]}\" is impossible.")

        if soda_copy["date_changed"] is not None:
            if ((datetime.strptime(soda_copy["date_changed"], _date_format)
                 - datetime.strptime(soda_copy["date_created"], _date_format)).total_seconds() < 0):
                raise Exception("date_created and date_changed: date_changed can't be before date_created.")
    # </editor-fold>

    # Arriving here means that no check has failed, thus the soda is valid.


def _check_fida(fida: List[dict]):
    """
    Check compliance of the fida with the fida guidelines,
    and the compliance of each soda in the fida with the soda guidelines.
    Returns only if the fida is valid.
    :param fida: The list of dictionaries to be checked.
    """

    fida_copy = fida.copy()
    found_duplicate = False

    def generate_combinations(fida: List[dict], target_key: str) -> List[dict]:
        result = []
        for item in fida:
            target_values = item[target_key]
            keys = list(target_values.keys())
            values = [target_values[k] if isinstance(target_values[k], list) else [target_values[k]] for k in keys]
            for combination in itertools.product(*values):
                new_item = {
                    **{k: item[k] for k in item if k not in {target_key}},
                    target_key: {keys[i]: combination[i] for i in range(len(keys))}
                }
                result.append(new_item)
        return result

    def find_duplicates(keys: list, fida: List[dict]):
        duplicates_info = {}
        for key in keys:
            unique_values = []
            duplicate_values = []
            for soda in fida:
                value = soda[key]
                if value in unique_values and value not in duplicate_values:
                    duplicate_values.append(value)
                elif value:
                    unique_values.append(value)
            if duplicate_values:
                duplicates_info.update({key: duplicate_values})
        return duplicates_info

    expanded_fida = generate_combinations(fida=fida_copy, target_key="location")

    # Check for and print individual location duplicates
    seen_locations = []
    for soda in expanded_fida:
        location_tuple = tuple(sorted(soda["location"].items()))
        if location_tuple in seen_locations:
            cusocos = [d.get("cusoco") for d in get({"location": dict(location_tuple)}, expanded_fida)]
            print(
                f"Multiple sodas with matching values found: "
                f"key: \"location\", "
                f"value: {dict(location_tuple)}, "
                f"cusocos: {list(set(cusocos))}")
            found_duplicate = True
        else:
            seen_locations.append(location_tuple)

    other_duplicates_info = find_duplicates(keys=["cusoco", "name", "date_created", "date_changed"], fida=fida_copy)
    if other_duplicates_info:
        found_duplicate = True
        for key, duplicate_values in other_duplicates_info.items():
            for value in duplicate_values:
                cusocos = [d.get("cusoco") for d in get({key: value}, fida_copy)]
                print(
                    f"Multiple sodas with matching values found: "
                    f"key: \"{key}\", "
                    f"value: {value}, "
                    f"cusocos: {list(set(cusocos))}")

    if found_duplicate:
        raise Exception(f"Duplicate values found.")

    for i in range(len(fida_copy)):
        soda = fida_copy[i]
        try:
            check_soda(soda)
        except Exception as e:
            print(f"Invalid soda in fida found: cusoco: {soda['cusoco']}, index: {i + 1}")
            raise e

    # Arriving here means that no check has failed, thus the soda is valid.


def add(soda: dict, on_duplicates_found: Literal["raise", "ignore", "overwrite"] = "raise") -> None:
    """
    Add a new container.\n
    Note that no dates are needed in the soda, as they are set here.\n
    :param soda: The sorting data, a dictionary that includes all keys listed above.
    :param on_duplicates_found: What to do when a container with the same cusoco is found:
    raise: raise an exception - ignore: don't do anything - overwrite: replace the duplicate container.
    """

    soda_copy = soda.copy()
    soda_new = _template_soda.copy()

    time.sleep(0.0001)

    soda_new.update(soda_copy)  # Replace the values in the soda template with the actual values.

    soda_new.update({  # Replace the two dates in the soda template with the correct dates.
        "date_created": datetime.now().strftime(_date_format),
        "date_changed": None
    })

    cusoco = soda_new["cusoco"]

    overwrite = False

    if exists({"cusoco": cusoco}):  # What to do if a container with the same cusoco already exists.
        if on_duplicates_found == "raise":
            raise Exception(f"The container #{cusoco} already exists.")

        elif on_duplicates_found == "ignore":
            return

        elif on_duplicates_found == "overwrite":
            overwrite = True  # Set a flag for later to instead change a container instead of appending it.

    check_soda(soda_new)

    if overwrite:
        change(cusoco=cusoco, soda=soda_new, overwrite_date_created=True)
    else:
        fida = _read()

        fida.append(soda_new)

        _check_fida(fida)

        _write(fida)


def change(cusoco: int, soda: dict, overwrite_date_created: bool = False) -> None:
    """
    Change one or more values of a certain container.
    :param cusoco: Cusoco of the container to be changed.
    :param soda: Dictionary of one or more key-value pairs to be changed.
    :param overwrite_date_created: If date_created should also be changed.
    """

    time.sleep(0.0001)

    soda_copy = soda.copy()

    soda_copy.pop("cusoco", None)
    soda_copy.pop("date_created", None)
    soda_copy.pop("date_changed", None)

    check_soda(soda=soda_copy, incomplete_soda=True)

    containers = get({"cusoco": cusoco})

    if not containers:
        raise Exception("No containers found to change.")

    container = containers[0]

    if overwrite_date_created:
        soda_copy["date_created"] = datetime.strftime(datetime.now(), _date_format)
        soda_copy["date_changed"] = None
    else:
        soda_copy["date_changed"] = datetime.strftime(datetime.now(), _date_format)

    container.update(soda_copy)

    _replace(search_soda={"cusoco": cusoco}, replacement_soda=container, replace_all=True)


def remove(cusoco: int) -> None:
    """
    Remove a container.
    :param cusoco: Cusoco of the container to remove.
    """

    if not exists(search_soda={"cusoco": cusoco}):
        raise Exception("No containers found to remove.")

    check_soda(soda={"cusoco": cusoco}, incomplete_soda=True)

    fida = _read()

    indexes = []
    for i in range(len(fida)):
        soda = fida[i]  # Iterate through all sodas.
        if soda["cusoco"] == cusoco:  # If search_soda fits into current soda,
            indexes.append(i)  # append the current soda's index to a list.

    del fida[indexes[0]]

    _check_fida(fida)

    _write(fida)


def save():
    """
    Actually save the file to the disc.
    """

    temp_filename = _data_path + ".tmp"

    sorted(_global_fida, key=itemgetter("cusoco"))

    with open(temp_filename, "w") as file:
        json.dump(_global_fida, file, indent=4)

    try:
        with open(temp_filename, "r") as file:
            fida = json.load(file)

        _check_fida(fida)
        for soda in fida:
            check_soda(soda)

    except:
        raise Exception(f"Temporary file corrupted, leaving {_data_path} unchanged.")

    shutil.move(temp_filename, _data_path)


def _post_code_fida_integrity_checks():
    _check_fida(_read())
    for i in _read():
        check_soda(i)


_post_code_fida_integrity_checks()
