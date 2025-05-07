import autodex

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
    }, on_duplicates_found="overwrite")
    y += 2

autodex.add(soda={
    "cusoco": 5,
    "storage_unit": "Parent",
    "container_type": "Child",
    "location": {
        "Cusoco": 2
    },
    "name": f"child 1",
    "description": "A child of #2.",
    "image_paths": [],
    "contents": []
}, on_duplicates_found="overwrite")

autodex.add(soda={
    "cusoco": 6,
    "storage_unit": "Parent",
    "container_type": "Child",
    "location": {
        "Cusoco": 2
    },
    "name": f"child 2",
    "description": "Another child, also of #2.",
    "image_paths": [],
    "contents": []
}, on_duplicates_found="overwrite")

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

print(autodex.get(search_soda={"contents": ['m4 screws']}, partial_contents=True))

print(autodex.get(search_soda={"description": "this"}, partial_description=True))

autodex.remove(cusoco=1)

autodex.save()  # Actually write the data to a disk.
