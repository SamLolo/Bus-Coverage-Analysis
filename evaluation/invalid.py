import geopandas as gpd
from common.data import OUT_DIR

invalid = gpd.read_file(OUT_DIR / "invalid_lsoas.gpkg")

print("Missing Bus Isochrone\n---------------------")
missing_bus = invalid[invalid['reason'] == "Missing bus isochrone"]
if missing_bus.shape[0] != 0:
    print(missing_bus)
else:
    print("No results")

print("\nMissing Car Isochrone\n---------------------")
missing_car = invalid[invalid['reason'] == "Missing car isochrone"]
if missing_car.shape[0] != 0:
    print(missing_car)
else:
    print("No results")
    
print("\nBus Isochrone Null Area\n-----------------------")
null_bus = invalid[invalid['reason'] == "Bus isochrone has null area"]
if null_bus.shape[0] != 0:
    print(null_bus)
else:
    print("No results")

print("\nCar Isochrone Null Area\n-----------------------")
null_car = invalid[invalid['reason'] == "Car isochrone has null area"]
if null_car.shape[0] != 0:
    print(null_car)
else:
    print("No results")

print("\nInvalid Ratio (> 1)\n-------------------")
invalid_ratio = invalid[invalid['reason'] == "Area ratio is greater than 1"]
if invalid_ratio.shape[0] != 0:
    print(invalid_ratio)
else:
    print("No results")