
# Autodex - The automatic Part Indexing System

Autodex helps with storing and keeping track of large amounts of items in places like workshops.

It works across different storage units, ziploc bags and containers, while also minimizing the amount written information per container or bag to simply an id, called cusoco - the custom sorting code.

This id is written on a sticker as both a QR-Code and a written number, and is placed on all containers.

During the initial registration of a new container or bag, the entire data, including contents, name, location, and more, gets stored in a file instead of anywhere physical.

This allows users to efficiently and rapidly find and store containers containing obscure or hard-to-describe contents.

Its purpose is to make cleaning up and sorting workshops for hobbyists and makers easier, 
and to know about all things you own.

## Important terms

storage unit - This is a piece of furniture like a shelf. Different storage units can have different amounts of space in different axies specified for containers. 

container - This means either a box or a child of a box, being a ziploc bag.

cusoco - The custom sorting code. It is the only identifier and is on every container.

fida - The file data. This is the overarching file where all sodas are stored. It is a list of dictionaries. It is normally in a variable and only written to disk when save() is called.

soda - The sorting data. This is the saved data of a container. It is a dictionary.

### What a soda looks like

```python
{
    "cusoco": 4,  # The index of the container.
    "storage_unit": "Small shelf",  # The piece of furniture it's stored in.
    "container_type": "9L transparent box",  # The container type.
    "location": {  # Where the container is located inside of the storage unit.
        "floor": 4,  # Different storage units accept different container types,
        "x": 7,  # some locations can be an integer,
        "y": [4, 5, 6]  # others can be a range of values, indicating that the container
                        # takes up the space of 3 y-units.
        },
    "name": "solenoid pneumatic valves",  # Something unique about it's contents.
    "description": "12vdc/24vdc", 
    "image_paths": ["45125.png", "41452.png"],
    "contents": ["Festo valve", "SMC valve", "Steam compatible valve", 283],
                                # Can also include cusocos of other containes
    "date_created": "2025-01-16T23:00:12.978108Z",  # These two dates are not needed 
    "date_changed": "2025-01-16T23:00:40.654869Z"   # when adding a container.
}
```

###

![App Screenshot](https://i.ibb.co/Lz4DKvbr/Page1-2.png)
## Usage/Examples

``` python
import Autodex.autodex as autodex  # Autodex reads from the actual file and checks it for any problems.

y = 1
for i in range(1, 4):
    autodex.add(soda={
        "cusoco": i,
        "storage_unit": "Some storage unit",
        "container_type": "A box",
        "location": {
            "Floor": 4,
            "X": 7,
            "Y": [y, y + 1],
            "Z": 2
        },
        "name": f"test {i}",
        "description": "This is where all somethings are stored.",
        "image_paths": [],
        "contents": ["festo valve", "smc valve", "steam compatible valve"]
    }, on_duplicates_found="ignore")
    y += 2

print(autodex.exists(search_soda={"storage_unit": "Some storage unit",
                                  "container_type": "A box",
                                  "location": {
                                      "Floor": 4,
                                      "X": 7,
                                      "Z": 2
                                  }}, partial_coords=True))

autodex.change(cusoco=1, soda={"name": "this is now changed!",
                               "description": "screw this!",
                               "contents": ["m4 screws", "m5 screws"]})

print(autodex.get(search_soda={"cusoco": 2}))

print(autodex.get(search_soda={"location": {"Floor": 4,
                                            "X": 7,
                                            "Y": [1, 2, 3],
                                            "Z": 2}}, partial_coords=True))

autodex.save()  # Actually write the data to a disk. Anything before this only gets written to a variable and will be lost in a power outage or crash.
```

## Setup

Directly in autodex.py, change the 3 variables at the top of the code to your desire, those being _data_path, _container_types and _storage_units.
It is advised to only ever read from these variables to ensure that the autodex data never gets corrupted in case of a power outage.
However, changing these variables doesn't break anything, but in the case that these were set incorrectly by a different program not only reading, but also writing to them, may result in an exception, as autodex has been made to keep the autodex data as safe from any problems as possible.

The autodex_data.json file contents are to be replaced with ["corruption safety override"] each time it is run until something has been written to it.
## License

[MIT](https://choosealicense.com/licenses/mit/)


## Feedback

If you have any questions, suggestions, feedback or issues, please tell me.


## Links

marluna2@posteo.de

https://www.youtube.com/@marluna_x

