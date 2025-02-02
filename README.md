
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
    "storage_unit": "small_shelf",  # The piece of furniture it's stored in.
    "container_type": "9_liter_transparent_box",  # The container type.
    "location": {  # Where the container is located inside of the storage unit.
        "floor": 4,  # Different storage units accept different container types,
        "x": 7,  # some locations can be an integer,
        "y": [4, 5, 6]  # others can be a range of values, indicating that the container
                        # takes up the space of 3 y-units.
        },
    "name": "solenoid pneumatic valves",  # Something unique about it's contents.
    "description": "12vdc/24vdc", 
    "image_paths": ["45125.png", "41452.png"],
    "contents": ["festo valve", "smc valve", "steam compatible valve", 283],
                                # Can also include cusocos of other containes
    "date_created": "2025-01-16T23:00:12.978108Z",  # These two dates are not needed 
    "date_changed": "2025-01-16T23:00:40.654869Z"   # when adding a container.
}
```

###

![App Screenshot](https://i.ibb.co/Lz4DKvbr/Page1-2.png)
## Usage/Examples

``` python
import autodex

autodex.add(soda={
    "cusoco": 4,
    "storage_unit": "small_shelf",
    "container_type": "greiner_small",
    "location": {
        "floor": 4,
        "x": 7,
        "y": [4, 5],
        "z": 1
    },
    "name": "solenoid pneumatic valves",
    "description": "12vdc/24vdc",
    "image_paths": [],
    "contents": ["festo valve", "smc valve", "steam compatible valve"]
}, on_duplicates_found="overwrite")

print(autodex.get(search_soda={"description": "12vdc/24vdc"}))

autodex.change(cusoco=4, soda={"name": "this is now changed!",
                               "contents": ["festo valve", "smc valve"]})

print(autodex.get(search_soda={"cusoco": 4}))

autodex.save()  # Actually write the data to a disk.
```

## License

[MIT](https://choosealicense.com/licenses/mit/)


## Feedback

If you have any questions or feedback, feel free to ask me.


## Links

marluna2@posteo.de

https://www.youtube.com/@marluna_x

