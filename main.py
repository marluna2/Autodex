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
        "Voltage": {"Vdc": [24]},
        "Power draw": {"W": [0.35, 1.5]}},
    "Categorical attributes": {
        "Manufacturer": ["Festo", "SMC"],
        "Valve type": ["3/2 way NC", "5/2 way monostable"]},
    "Image paths": ["img1351.jpg"],
    "F3D folder path": "f3d_images_14",
}

autodex_V2.load_file()  # Load fida and header from file on disk into global variables.

print(autodex_V2.add_soda(soda, commit=False))
# By doing commit=False, it doesn't actually add the soda, but returns errors as if it did.
# This way we can see if there are problems with the soda.

if "y" == input("Add soda? (Y/N)").lower():
    returned = autodex_V2.add_soda(soda, commit=True)

    if type(returned) is list:
        print("Successful")
    else:
        print(returned)

for soda in autodex_V2.get_fida():  # Get list of all sodas,
    print(soda)                     # and print each soda individually.

autodex_V2.save_file()  # Save fida and header to file on disk.
