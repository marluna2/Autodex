import datetime
import json
import shutil
from operator import itemgetter
from pathlib import Path
from typing import Literal, List, Union

_save_path = "autodex_data.json"

_template_soda = {
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
    "F3D folder path": str,
    "Date created": str,
    "Date changed": str
}
_template_header = {
    "Autodex version": str,
    "Last saved": str,
    "Date format": str,
    "Storage units": dict,
    "Container types": dict,
    "Unit conversions": dict,
    "Numeric attributes": dict
}
_global_fida = []
_global_header = {}


class AutodexException(Exception):
    """Used to separate intentional from unintentional exceptions by removing catch-all try-except statements"""

    pass


def standalone_check(soda: dict, header: [dict, None] = None) -> [None, str]:
    """Check if a soda is valid, without taking stored sodas into consideration"""

    if header is None:
        header = _global_header.copy()

    date_format = header["Date format"]
    container_types = header["Container types"]
    storage_units = header["Storage units"]

    if type(soda) is not dict:
        return f"E014 Soda must be dict, not {type(soda)}"

    if soda.keys() != _template_soda.keys():
        invalid_keys = []
        missing_keys = []

        soda_keys = soda.keys()
        template_keys = _template_soda.keys()

        for soda_key in soda_keys:
            if soda_key not in template_keys:
                invalid_keys.append(soda_key)

        for template_key in template_keys:
            if template_key not in soda_keys:
                missing_keys.append(template_key)

        return f"E015 Soda has invalid {invalid_keys} or missing {missing_keys} keys"

    for key, value in soda.items():

        if type(value) is not _template_soda[key]:
            return f"E016 {key} value data type must be {_template_soda[key]}, not {type(value)}"

    # region Name

    if not soda["Name"].strip():
        return "E017 Name mustn't be empty"

    # endregion
    # region Cusoco

    soda_cusoco = soda["Cusoco"]

    if soda_cusoco < 1:
        return f"E018 Cusoco must be greater than 0, not {soda_cusoco}"

    # endregion
    # region Storage unit

    soda_storage_unit = soda["Storage unit"]

    if soda_storage_unit not in storage_units.keys():
        return f"E019 Storage unit {soda_storage_unit} isn't listed in file header"

    # endregion
    # region Container type

    soda_container_type = soda["Container type"]

    if soda_container_type not in container_types.keys():
        return f"E020 Container type {soda_container_type} isn't listed in file header"

    if soda_storage_unit not in container_types[soda_container_type].keys():
        return (f"E021 Storage unit {soda_storage_unit} is incompatible with container type"
                f" {soda_container_type}")

    # endregion
    # region Contents, Tags, Image paths

    for key in ("Contents", "Tags", "Image paths"):

        seen = []
        soda_key = soda[key]
        for i in soda_key:

            if type(i) is not str:
                return f"E022 {key} must only contain str, not {type(i)}"

            if i in seen:
                return f"E023 {key} mustn't contain duplicates: {i}"

            if not i.strip():
                return f"E024 {key} mustn't contain empty items"

            seen.append(i)

    # endregion
    # region Numeric attributes

    for key, value in soda["Numeric attributes"].items():

        if type(value) is not dict:
            return f"E025 Numeric attributes {key} must be in dict, not {type(value)}"

        if key not in header["Numeric attributes"].keys():
            return f"E026 Invalid numeric attribute: {key}"

        if not value:
            return f"E119 Numeric attribute {key} mustn't be empty"

        possible_units = get_unit_conversions(header["Numeric attributes"][key], True, header)

        for i in value.keys():

            if i not in possible_units:
                return f"E027 The numeric attribute {key} unit {i} is not compatible with {key}"

        for u, i in value.items():

            if type(i) is not list:
                return f"E028 Numeric attribute {key} value {u} must be list, not {type(i)}"

            if not i:
                return f"E029 Numeric attribute {key} value {u} mustn't be empty"

            seen = []
            for j in i:

                if type(j) not in (int, float):
                    return f"E030 Numeric attribute {key} value {u} must be int or float, not {type(j)}"

                if j in seen:
                    return f"E032 Numeric attribute {key} value {u} mustn't have duplicates in it"

                seen.append(j)

    # endregion
    # region Categorical attributes

    for key, value in soda["Categorical attributes"].items():

        if type(value) is not list:
            return f"E033 Categorical attribute {key} values must be in list, not {type(value)}"

        seen = []
        for i in value:

            if type(i) is not str:
                return f"E034 Categorical attribute {key} value {i} must be str, not {type(i)}"

            if not i.strip():
                return f"E035 Categorical attribute {key} mustn't be empty"

            if i in seen:
                return f"E036 Categorical attribute {key} contains duplicates: {i}"

            seen.append(i)

    # endregion
    # region Image paths

    for i in soda["Image paths"]:

        if not Path(i).exists():
            return f"E037 Image path not found: {i}"

        if not i.endswith((".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff", ".webp", ".bmp", ".svg")):
            return f"E038 Image path must lead to an image type file: {i}"

    # endregion
    # region F3D folder path

    soda_f3d_folder_path = soda["F3D folder path"]

    if soda_f3d_folder_path:

        path = Path(soda_f3d_folder_path)

        if not path.exists():
            return f"E039 F3D folder path not found: {str(path.absolute())}"

        if not path.is_dir():
            return f"E040 F3D folder path isn't a directory: {str(path.absolute())}"

        for i in path.iterdir():
            if not i.is_dir():
                return f"E041 F3D folder mustn't contain files: {str(path.absolute())}"

        for i in path.iterdir():
            for j in i.iterdir():

                if j.is_dir():
                    return f"E042 F3D image group contains folders: {str(path.absolute())}"

                if not str(j).endswith((".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff", ".webp", ".bmp", ".svg")):
                    return f"E043 F3D image group contains non-image type file: {str(path.absolute())}"

    # endregion
    # region Location

    limits = storage_units[soda_storage_unit]
    size = container_types[soda_container_type][soda_storage_unit]
    location = soda["Location"]

    if limits.keys() != location.keys():
        return f"E044 Invalid location keys"

    location_plus_size = location.copy()

    for key, value in size.items():
        location_plus_size[key] += value - 1

    for key, value in location.items():
        key_limits = limits[key]
        if value < key_limits[0] or value > key_limits[1]:
            return f"E045 Base location out of bounds: {key}: {value} doesn't fit in {key_limits}"
        if type(value) is not int:
            return f"E046 Location {key} must be int, not {type(value)}"

    for key, value in location_plus_size.items():
        key_limits = limits[key]
        if value < key_limits[0] or value > key_limits[1]:
            return (f"E047 Location combined with container size out of bounds: {key}: {value} doesn't fit in"
                    f" {key_limits}")

    # endregion
    # region Date created

    soda_date_created = soda["Date created"]

    if not soda_date_created:
        return "E048 Creation date mustn't be empty"

    try:
        date_created = datetime.datetime.strptime(soda_date_created, date_format)

    except ValueError:
        return f"E049 Invalid creation date: {soda_date_created}"

    if date_created > datetime.datetime.now():
        return f"E050 Creation date mustn't be in the future: {soda_date_created}"

    # endregion
    # region Date changed

    soda_date_changed = soda["Date changed"]

    if soda_date_changed:

        try:
            date_changed = datetime.datetime.strptime(soda_date_changed, date_format)

        except ValueError:
            return f"E051 Invalid change date: {soda_date_changed}"

        if date_changed > datetime.datetime.now():
            return f"E052 Change date mustn't be in the future: {soda_date_changed}"

    # endregion


def collective_check(soda: dict, fida: [List[dict], None] = None, header: [dict, None] = None) -> [None, str]:
    """Check if a soda is valid, and if it doesn't have matching values of existing sodas"""

    if fida is None:
        fida = _global_fida.copy()

    if header is None:
        header = _global_header.copy()

    container_types = header["Container types"]

    standalone_return = standalone_check(soda, header)
    if standalone_return:
        return f"E053 {standalone_return}"

    for i in fida:

        if i["Cusoco"] == soda["Cusoco"]:
            return f"E054 Cusoco = {soda['Cusoco']} already used"

        if i["Name"] == soda["Name"]:
            return f"E009 Name = {soda['Name']} already used by #{i['Cusoco']}"

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
            return f"E055 Location is overlapping #{i['Cusoco']}'s location"


def fida_check(fida: List[dict], header: [dict, None] = None) -> [None, str]:
    """Check if fida is fully valid"""

    for i in fida:

        fida_copy = fida.copy()
        fida_copy.remove(i)

        check_return = collective_check(i, fida_copy, header)
        if check_return:
            return f"E056 Soda #{i['Cusoco']}: {check_return}"


def _header_check(header: dict, check_all: bool = True) -> [None, str]:
    """Checks if header is valid"""

    modified_template_header = _template_header.copy()
    if not check_all:
        modified_template_header.pop("Last saved")
        modified_template_header.pop("Autodex version")

    if type(header) is not dict:
        return f"E057 Header must be dict, not {type(header)}"

    # Top-level key check
    if header.keys() != modified_template_header.keys():
        invalid_keys = []
        missing_keys = []

        header_keys = header.keys()
        template_keys = modified_template_header.keys()

        for header_key in header_keys:
            if header_key not in template_keys:
                invalid_keys.append(header_key)

        for template_key in template_keys:
            if template_key not in header_keys:
                missing_keys.append(template_key)

        return f"E058 Header has invalid {invalid_keys} or missing {missing_keys} keys"

    # Top-level data type check
    for key, value_type in modified_template_header.items():
        if type(header[key]) is not value_type:
            return f"E059 Header {header[key]} must be {value_type}, not {type(header[key])}"

    # Last saved and date format check
    try:
        datetime.datetime.strftime(datetime.datetime.now(), header["Date format"])
    except ValueError:
        return f"E060 Invalid date format: {header['Date format']}"

    if check_all:
        try:
            datetime.datetime.strptime(header["Last saved"], header["Date format"])
        except ValueError:
            return f"E061 Last saved invalid: {header['Last saved']}"

    # In-depth storage units check
    for storage_unit, value in header["Storage units"].items():

        if type(value) is not dict:
            return (f"E062 Storage unit {storage_unit} axes and their limits must be provided in a dict with axes as "
                    f"keys and their limits as values: {value} must be dict, not {type(value)}")

        for axis, limit_values in value.items():

            if type(limit_values) is not list:
                return (f"E063 Storage unit position limit values for each axis must be in a list, not "
                        f"{type(limit_values)}")

            if len(limit_values) != 2:
                return (f"E064 Storage unit position limit values for each axis must be provided in a list with a "
                        f"length of 2, not {len(limit_values)}")

            for i in limit_values:
                if type(i) is not int:
                    return f"E065 Storage unit position limit values for each axis must be int, not {type(i)}"

            if limit_values[0] > limit_values[1]:
                return (f"E066 The first value mustn't be higher "
                        f"than the second value for the storage unit position limits for each axis "
                        f"({storage_unit}: {axis}: {limit_values})")

    # In-depth container types check
    for container_type, value in header["Container types"].items():

        if type(value) is not dict:
            return f"E067 Container sizes must be in dict, not {type(value)}"

        for storage_unit, sizes in value.items():

            if storage_unit not in header["Storage units"].keys():
                return f"E068 Container size dict has invalid storage unit: {storage_unit}"

            if type(sizes) is not dict:
                return f"E069 Container size dicts must only contain dicts, not {type(sizes)}"

            for axis_name, axis_size in sizes.items():

                if axis_name not in header["Storage units"][storage_unit]:
                    return (f"E070 Container size axis name invalid for associated storage unit: "
                            f"{({axis_name: axis_size})}")

                if type(axis_size) is not int:
                    return f"E071 Container sizes must be int, not {type(axis_size)}"

                if axis_size < 1:
                    return f"E072 Container size must be greater than 0, not {axis_size}"

                axis_limits = header["Storage units"][storage_unit][axis_name]
                axis_max_size = axis_limits[1] - axis_limits[0] + 1

                if axis_size > axis_max_size:
                    return f"E073 Container too large for associated storage unit: {({axis_name: axis_size})}"

    # In-depth unit conversions check
    seen_units = list(header["Unit conversions"].keys())
    for base_unit, value in header["Unit conversions"].items():

        if not base_unit.strip():
            return f"E074 Base unit name mustn't be empty"

        if base_unit.strip() != base_unit:
            return f"E075 Base unit name mustn't have leading or trailing spaces"

        if type(value) is not dict:
            return f"E076 Unit conversion must be dict, not {type(value)} ({base_unit})"

        for sub_unit, sub_conversion in value.items():

            if not sub_unit.strip():
                return f"E077 Sub-unit name mustn't be empty for ({base_unit})"

            if sub_unit.strip() != sub_unit:
                return f"E078 Sub-unit name mustn't contain leading or trailing spaces ({base_unit})"

            if sub_unit == base_unit:
                return f"E079 Sub-unit can't be the same as base unit ({base_unit})"

            if type(sub_conversion) is not dict:
                return f"E080 Sub-unit conversion must be dict, not {type(sub_conversion)} ({base_unit})"

            if not sub_conversion:
                return f"E081 Sub-unit conversion dict mustn't be empty ({base_unit})"

            for i, j in sub_conversion.items():

                if i not in ["+", "-", "*", "/"]:
                    return f"E082 Sub-unit conversion dict must only have + - * /, not {i} ({base_unit})"

                if type(j) not in [int, float]:
                    return f"E083 Sub-unit conversion values must be int or float, not {type(j)} ({base_unit})"

            operations = sub_conversion.keys()

            if "+" in operations and "-" in operations:
                return f"E084 Sub-unit conversion dict mustn't have both + and - in it ({base_unit})"

            if "*" in operations and "/" in operations:
                return f"E085 Sub-unit conversion dict mustn't have both * and / in it ({base_unit})"

            if sub_unit in seen_units:
                return f"E086 Sub-unit has already been declared as a unit ({base_unit})"

            seen_units.append(sub_unit)

    # In-depth numeric attributes check
    for key, value in header["Numeric attributes"].items():

        if type(value) is not str:
            return f"E087 Numeric attribute units must be str, not {type(value)} ({key})"

        if value.strip() != value:
            return f"E088 Numeric attribute units mustn't contain leading or trailing spaces ({key})"

        unit_check_return = unit_check(value, False, header)
        if unit_check_return:
            return f"E089 Invalid numeric attribute unit: {unit_check_return} ({key})"


def _file_check(path: str) -> [None, str]:
    """Checks integrity of fida and header of file"""

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except json.decoder.JSONDecodeError as error:
        return f"E090 Couldn't decode file: {error}"

    except FileNotFoundError:
        return f"E091 File not found"

    if len(data) != 2:
        return f"E092 Length of outer list in file must be 2, not {len(data)}"

    header = data[0]
    fida = data[1]

    if type(header) is not dict:
        return f"E093 Header must be a dict, not {type(header)}"
    if type(fida) is not list:
        return f"E094 Fida must be a list, not {type(fida)}"

    header_check_return = _header_check(header)
    if header_check_return:
        return f"E095 Header: {header_check_return}"

    fida_check_return = fida_check(fida, header)
    if fida_check_return:
        return f"E096 Fida: {fida_check_return}"


def unit_check(value: str, has_numbers: bool = True, header: [dict, None] = None) -> [None, str]:
    """Checks if unit or value is valid"""

    if header is None:
        header = _global_header

    value = value.strip()

    if has_numbers:
        if not value.startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                                 ".0", ".1", ".2", ".3", ".4", ".5", ".6", ".7", ".8", ".9",
                                 "-0", "-1", "-2", "-3", "-4", "-5", "-6", "-7", "-8", "-9",
                                 "-.0", "-.1", "-.2", "-.3", "-.4", "-.5", "-.6", "-.7", "-.8", "-.9"
                                 )):
            return "E097 Value must start with a number"

        number_str = ""
        unit = ""

        end_of_number = False
        for i in value:

            if i not in "0123456789.-":
                end_of_number = True

            if end_of_number:
                unit += i
            else:
                number_str += i

        try:
            float(number_str)
        except ValueError:
            return "E098 Invalid number"

    else:
        unit = value

    unit = unit.strip()

    seen = False
    for key, value in header["Unit conversions"].items():

        if unit == key or unit in value.keys():
            seen = True
            break

    if not seen:
        return "E099 Invalid unit"


def separate_number_and_unit(value: str) -> List[Union[float, str]]:
    """Separates value into float and unit, raises exception if value is invalid"""

    value = value.strip()

    if not value.startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                             ".0", ".1", ".2", ".3", ".4", ".5", ".6", ".7", ".8", ".9",
                             "-0", "-1", "-2", "-3", "-4", "-5", "-6", "-7", "-8", "-9",
                             "-.0", "-.1", "-.2", "-.3", "-.4", "-.5", "-.6", "-.7", "-.8", "-.9"
                             )):
        raise AutodexException("E001 Value must start with a number")

    number_str = ""
    unit = ""

    end_of_number = False
    for i in value:

        if i not in "0123456789.-":
            end_of_number = True

        if end_of_number:
            unit += i
        else:
            number_str += i

    try:
        number = float(number_str)
    except ValueError:
        raise AutodexException("E002 Invalid number")

    unit = unit.strip()

    seen = False
    for key, value in _global_header["Unit conversions"].items():

        if unit == key or unit in value.keys():
            seen = True
            break

    if not seen:
        raise AutodexException("E003 Invalid unit")

    return [number, unit]


def get_unit_conversions(unit: str, with_self: bool = False, header: [dict, None] = None) -> list:
    """Returns list of all units that the given unit can be converted to, with or without itself"""

    if header is None:
        header = _global_header

    unit = unit.strip()

    for key, value in header["Unit conversions"].items():

        if unit == key or unit in value.keys():
            possible_units = list(value.keys())
            possible_units.insert(0, key)

            if not with_self:
                possible_units.remove(unit)

            return possible_units

    raise AutodexException("E004 Invalid unit")


def convert_unit(old_value: str, new_unit, with_prefix: bool = False) -> [int, str]:
    """Converts old_value to new_unit, raises exception if values are invalid or incompatible"""

    conversions = _global_header["Unit conversions"]

    try:
        old_number, old_unit = separate_number_and_unit(old_value)
    except AutodexException:
        raise AutodexException("E005 Invalid value")

    try:
        possible_units = get_unit_conversions(new_unit, True)
    except AutodexException:
        raise AutodexException("E006 New unit invalid")

    if old_unit not in possible_units:
        raise AutodexException("E007 Old unit incompatible with new unit")

    if old_unit not in conversions.keys():
        for key, values in conversions.items():

            if old_unit in values.keys():
                base_unit = key
                old_conversion_dict = values[old_unit]

        base_number = old_number

        if "+" in old_conversion_dict.keys():
            base_number -= old_conversion_dict["+"]
        elif "-" in old_conversion_dict.keys():
            base_number += old_conversion_dict["-"]

        if "*" in old_conversion_dict.keys():
            base_number /= old_conversion_dict["*"]
        elif "/" in old_conversion_dict.keys():
            base_number *= old_conversion_dict["/"]

    else:
        base_unit = old_unit
        base_number = old_number

    new_number = base_number

    if not new_unit == base_unit:
        new_conversion_dict = conversions[base_unit][new_unit]

        if "*" in new_conversion_dict.keys():
            new_number *= new_conversion_dict["*"]
        elif "/" in new_conversion_dict.keys():
            new_number /= new_conversion_dict["/"]

        if "+" in new_conversion_dict.keys():
            new_number += new_conversion_dict["+"]
        elif "-" in new_conversion_dict.keys():
            new_number -= new_conversion_dict["-"]

    if with_prefix:
        new_number = str(new_number) + new_unit

    return new_number


def change_numeric_attributes(
        attribute: str,
        operation:
        Literal["change standard unit", "change unit bases", "rename", "merge", "add", "delete"],
        commit: bool,
        unit: str = None,
        rename_to: str = None,
        merge_into: str = None) -> [str, list, Literal[True]]:
    """Change numeric attributes in the header. Makes changes to fida if required"""

    numeric_attributes = _global_header["Numeric attributes"]

    if operation in ["change standard unit", "change unit bases", "rename", "merge", "delete"]:

        if attribute not in numeric_attributes.keys():
            return "E100 Invalid attribute"

    if operation in ["change standard unit", "change unit bases", "add"]:

        if unit_check(unit, False):
            return "E101 Invalid unit"

    if operation in ["change standard unit", "change unit bases"]:

        if unit == numeric_attributes[attribute]:
            return "E102 Unit already saved"

    if operation == "change standard unit":

        if unit not in get_unit_conversions(numeric_attributes[attribute], True):
            return "E103 Unit is in a different unit base"

        if commit:
            _global_header["Numeric attributes"][attribute] = unit

        return True

    if operation == "change unit bases":

        if unit in get_unit_conversions(numeric_attributes[attribute], True):
            return "E104 Unit is in the same unit base"

        _global_header["Numeric attributes"][attribute] = unit.strip()

        changes_list = []
        for index in range(len(_global_fida)):
            soda = _global_fida[index]

            if attribute in soda["Numeric attributes"].keys():
                changes_list.append(soda["Cusoco"])

                if commit:
                    soda["Numeric attributes"].pop(attribute)
                    soda["Date changed"] = datetime.datetime.strftime(datetime.datetime.now(),
                                                                      _global_header["Date format"])

        return changes_list

    if operation == "rename":

        if attribute == rename_to:
            return "E105 New attribute name mustn't be the same"

        if rename_to in numeric_attributes.keys():
            return "E106 New attribute name already taken"

        if not rename_to.strip():
            return "E107 New attribute name mustn't be empty"

        changes_list = []
        for index in range(len(_global_fida)):
            soda = _global_fida[index]

            if attribute in soda["Numeric attributes"].keys():
                changes_list.append(soda["Cusoco"])

                if commit:
                    soda["Numeric attributes"][rename_to] = soda["Numeric attributes"].pop(attribute)
                    soda["Date changed"] = datetime.datetime.strftime(datetime.datetime.now(),
                                                                      _global_header["Date format"])

        if commit:
            _global_header["Numeric attributes"][rename_to] = _global_header["Numeric attributes"].pop(attribute)

        return changes_list

    if operation == "merge":

        if merge_into not in numeric_attributes.keys():
            return "E108 Invalid merge-into attribute"

        if merge_into == attribute:
            return "E109 Attribute mustn't merge with itself"

        if numeric_attributes[attribute] not in get_unit_conversions(numeric_attributes[merge_into], True):
            return "E110 Attributes must have the same unit base"

        changes_list = []
        for index in range(len(_global_fida)):
            soda = _global_fida[index]

            if attribute in soda["Numeric attributes"].keys():
                changes_list.append(soda["Cusoco"])

                if commit:
                    if merge_into in soda["Numeric attributes"].keys():

                        old_dict = soda["Numeric attributes"].pop(attribute)
                        new_dict = soda["Numeric attributes"][merge_into]
                        merged_dict = new_dict.copy()

                        for key, value in old_dict.items():

                            if key in new_dict.keys():
                                merged_dict[key] = list(set(merged_dict[key]).union(value))

                            else:
                                merged_dict[key] = value

                        soda["Numeric attributes"][merge_into] = merged_dict

                    else:
                        soda["Numeric attributes"][merge_into] = soda["Numeric attributes"].pop(attribute)

                    soda["Date changed"] = datetime.datetime.strftime(datetime.datetime.now(),
                                                                      _global_header["Date format"])

        if commit:
            _global_header["Numeric attributes"].pop(attribute)

        return changes_list

    if operation == "add":

        if attribute in numeric_attributes.keys():
            return "E111 Attribute exists already"

        attribute = attribute.strip()

        if not attribute:
            return "E112 Attribute name mustn't be empty"

        if commit:
            _global_header["Numeric attributes"][attribute] = unit.strip()

        return True

    if operation == "delete":

        changes_list = []
        for index in range(len(_global_fida)):
            soda = _global_fida[index]

            if attribute in soda["Numeric attributes"].keys():
                changes_list.append(soda["Cusoco"])

                if commit:
                    soda["Numeric attributes"].pop(attribute)

                    soda["Date changed"] = datetime.datetime.strftime(datetime.datetime.now(),
                                                                      _global_header["Date format"])

        if commit:
            _global_header["Numeric attributes"].pop(attribute)

        return changes_list

    raise AutodexException(f"E008 Invalid operation: {operation}")


def add_soda(soda: dict, commit: bool) -> [str, list]:
    """Creates a new soda in global_fida"""

    soda = soda.copy()

    if "Date created" in soda.keys() or "Date changed" in soda.keys():
        return "E113 Soda mustn't contain Date created or Date changed"

    soda["Date created"] = datetime.datetime.strftime(datetime.datetime.now(), _global_header["Date format"])
    soda["Date changed"] = ""

    check_return = collective_check(soda)

    if check_return:
        return f"E114 {check_return}"

    if commit:
        _global_fida.append(soda)

    return [soda["Cusoco"]]


def delete_soda(cusoco: int, commit: bool) -> [str, list]:
    """Deletes a soda in global_fida"""

    seen = False
    for soda in _global_fida:

        if soda["Cusoco"] == cusoco:
            seen = True
            break

    if not seen:
        return "E115 Invalid cusoco"

    if commit:
        for index in range(len(_global_fida)):
            soda = _global_fida[index]

            if soda["Cusoco"] == cusoco:
                _global_fida.pop(index)
                break

    return [cusoco]


def change_soda(cusoco: int, changed_soda: dict, commit: bool) -> [str, list]:
    """Changes a soda in global_fida"""

    global _global_fida

    if "Date created" in changed_soda.keys() or "Date changed" in changed_soda.keys():
        return "E116 Soda mustn't contain Date created or Date changed"

    test_fida = _global_fida.copy()

    for index in range(len(test_fida)):
        soda = test_fida[index]

        if soda["Cusoco"] == cusoco:
            test_fida.pop(index)

            new_soda = soda.copy()
            new_soda.update(changed_soda)
            new_soda["Date changed"] = datetime.datetime.strftime(datetime.datetime.now(),
                                                                  _global_header["Date format"])

            check_return = collective_check(new_soda, test_fida)
            if check_return:
                return f"E117 check_return"

            if commit:
                test_fida.append(new_soda)

                _global_fida = test_fida.copy()

            return [cusoco]

    return "E118 Invalid cusoco"


def get_fida() -> List[dict]:
    """Copies global_fida. Use this instead of global_fida.copy() to avoid working with global_fida directly"""

    return _global_fida.copy()


def save_file(path: str = _save_path, fida: [list, None] = None, header: [dict, None] = None) -> [None, str]:
    """Saves global_fida and global_header to the file at the path"""

    if fida is None:
        fida = _global_fida.copy()

    if header is None:
        header = _global_header.copy()

    fida_check_return = fida_check(fida)
    if fida_check_return:
        raise AutodexException(f"E010 Fida: {fida_check_return}")

    header_check_return = _header_check(header)
    if header_check_return:
        raise AutodexException(f"E011 Header: {header_check_return}")

    final_header = header.copy()
    final_header["Last saved"] = datetime.datetime.now().strftime(header["Date format"])

    final_fida = sorted(fida.copy(), key=itemgetter("Cusoco"))

    final_data = [final_header, final_fida]

    temp_save_path = path + ".tmp"

    with open(temp_save_path, "w", encoding="utf-8") as temp_file:
        json.dump(final_data, temp_file, indent=2)

    file_check_return = _file_check(temp_save_path)
    if file_check_return:
        raise AutodexException(f"E012 Temp save file: {file_check_return}")

    shutil.move(temp_save_path, _save_path)


def load_file(path: str = _save_path) -> None:
    """Loads contents of a file into global_header and global_fida"""

    global _global_header, _global_fida, _save_path

    file_check_return = _file_check(path)
    if file_check_return:
        raise AutodexException(f"E013 Couldn't load file: {file_check_return}")

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    _global_header = data[0]
    _global_fida = data[1]

    _save_path = path
