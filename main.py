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
