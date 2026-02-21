
# Autodex - The automatic part indexing system

Autodex helps with storing and keeping track of large amounts of items in places like workshops.

It works across different storage units and containers, while also minimizing the amount of text on each container to simply an id, called cusoco - the custom sorting code.

This id is written on a sticker and is placed on all containers.

During the initial registration of a new container, the entire data, including contents, name, location, and more, gets stored in a file instead of anywhere physical.

This allows users to efficiently and rapidly find and store containers containing obscure or hard-to-describe contents.

Its purpose is to make cleaning up and sorting workshops for hobbyists and makers easier, and to know about everything you own.

Because everything is stored in a single file, it's very easy to exchange data of entire warehouses with other devices without the need for setup.

It has been re-written from scratch, featuring better and much more readable code, along with more information able to be stored about each container.

You can now store numeric attributes like 12V, 10cm or 3kg, which allows you to sort the list of containers by any of these attributes, and even convert between different units.


## Important terms

cusoco - The custom sorting code. It is the only identifier and must be on every container.

storage unit - This is a piece of furniture like a shelf. Different storage units can have different amounts of space in different axes specified for containers. 

container - A single box for storing stuff. Every container type can have different sizes for different storage units.

soda - The sorting data. This is the full saved data of a single container. It is a dictionary.

fida - The file data. This is where all sodas are stored, so a list of dicts.

header - A dict where all information about the soda structure is stored, so storage units, data format, and more.

file - The json file where header and fida are stored. It is a list of header first and fida second. This file is the only place where data is stored besides variables.

f3d - Short for Fake 3D, this is a group of pictures taken at many angles around an object, which is used to create the illusion that the object is a real 3D file instead of just images.


### What a soda looks like

```python
{
    "Cusoco": 14, # The container's id.
    "Storage unit": "Small wood shelf", # Where the container is stored.
    "Container type": "Blue box S", # What the container is.
    "Location": {"Floor": 2, "X": 4, "Depth": 1}, # Where in the storage unit it is stored.
    "Name": "Solenoid air valves", # Something to identify the container.
    "Description": "Some of the seals might need to be replaced", # Notes about contents, can be empty: "".
    "Contents": ["CPE18-M1H-5L-1/4", "OT-SMC064843"], # What is in the container, can be empty: [].
    "Tags": ["Valve", "Solenoid", "Pneumatic", "Electromagnetic", "Electric", "Electromechanical", "Mechanical"], # What categories the contents fall under.
    "Numeric attributes": { # New feature. Used for sorting and filtering.
        "Max pressure": {"bar": [10, 7]},
        "Min pressure": {"bar": [2.5, 0]},
        "Voltage DC": {"V": [24]},
        "Power": {"W": [0.35, 1.5]}},
    "Categorical attributes": { # New feature. Used for sorting and filtering.
        "Manufacturer": ["Festo", "SMC"],
        "Valve type": ["3/2 way NC", "5/2 way monostable"]},
    "Image paths": ["img1234.jpg"], # List of images for the contents of the container.
    "F3D folder path": "images_1234", # New feature. The path leads to a folder containing a folder. Each of the folders is for one object each, and contains many images of it.
    "Date created": "2025-12-27T19:48:21.569113Z", # Date of creation.
    "Date changed": "2025-12-28T20:22:36.310473Z"  # Last changed date.
}

```

### 

![image](https://github.com/user-attachments/assets/dd3e1f34-a876-424c-8d39-0d33091552ba)


## Usage/Examples

``` python
import autodex_V2

soda = {
    "Cusoco": 14,
    "Storage unit": "Small wood shelf",
    "Container type": "Blue box S",
    "Location": {"Floor": 2, "X": 4, "Depth": 1},
    "Name": "Solenoid air valves",
    "Description": "Some of the seals might need to be replaced",
    "Contents": ["CPE18-M1H-5L-1/4", "OT-SMC064843"],
    "Tags": ["Valve", "Solenoid", "Pneumatic", "Electromagnetic", "Electric", "Electromechanical", "Mechanical"],
    "Numeric attributes": {
        "Max pressure": {"bar": [10, 7]},
        "Min pressure": {"bar": [2.5, 0]},
        "Voltage DC": {"V": [24]},
        "Power": {"W": [0.35, 1.5]}},
    "Categorical attributes": {
        "Manufacturer": ["Festo", "SMC"],
        "Valve type": ["3/2 way NC", "5/2 way monostable"]},
    "Image paths": [],
    "F3D folder path": "",
}

autodex_V2.load_file()  # Load fida and header from file on disk into global variables.

message = autodex_V2.add_soda(soda, commit=False)
# By doing commit=False, it doesn't actually add the soda, but returns errors as if it did.
# This way we can see if there are problems with the soda.

print(message)

if type(message) is list:
    if "y" == input("Add soda? (Y/N)").lower():
        returned = autodex_V2.add_soda(soda, commit=True)

        if type(returned) is list:
            print("Successful")
        else:
            print(returned)

for soda in autodex_V2.get_fida():  # Get list of all sodas,
    print(soda)                     # and print each soda individually.

autodex_V2.save_file()  # Save fida and header to file on disk.
```


## Setup

To specify new storage units, container types, or more, go into your safe file (normally "autodex_data.json").
The file consists of the header at the top and the fida at the bottom.
The header is where values about how the sodas are stored is specified.
Most of the values in the header can't be changed by the program, because changes could destroy large amounts of data,
and changes are not supposed to be common.

Changing the header might result in errors, because existing sodas will still have the old header values.
This is why change_numeric_attributes exists, which updates all old soda values to prevent errors.


## License

[MIT](https://choosealicense.com/licenses/mit/)


## Feedback

If you have any questions, suggestions, feedback or issues, feel free to message me.


## Links

marluna2@posteo.de

https://www.youtube.com/@marluna_x

