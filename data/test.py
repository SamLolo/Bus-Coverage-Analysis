import os
import pandas as pd
from zipfile import ZipFile

PATH = os.path.dirname(os.path.realpath(__file__))


with ZipFile(f"{PATH}/raw/itm_england_gtfs.zip") as zip:
    trips = pd.read_csv(zip.open("trips.txt"))
    stop_times = pd.read_csv(zip.open("stop_times.txt"))
    feed_info = pd.read_csv(zip.open("feed_info.txt"))


def check_hours(time: str, threshold: int):
    hours = int(time.split(":")[0])
    if hours >= threshold:
        return True
    else:
        return False
    

def increment_trip_id(id: str):
    new_id = id[:-1] + str(int(id[-1]) + 1)
    return new_id


def decrease_day(time: str):
    hour, min, sec = time.split(":")
    if int(hour) >= 24:
        return f"{int(hour) - 24:02d}:{min}:{sec}"
    else:
        return f"{hour}:{min}:{sec}"


bad_stops = stop_times.loc[stop_times["departure_time"].apply(lambda x: check_hours(x, 72))].copy()
bad_stops.drop_duplicates("trip_id", inplace=True)

new_trips = []
for trip_id in bad_stops["trip_id"].values:
    stops: pd.DataFrame = stop_times.loc[stop_times["trip_id"] == trip_id].copy()
    
    stops.sort_values("stop_sequence", inplace=True)
    stops["trip_id"] = stops['trip_id'] + "_d1"
    
    stop_times = stop_times.loc[stop_times["trip_id"] != trip_id]
    
    new_trips.append(stops)

print("Unsplit:")
for x in new_trips:
    print(x)

split = False
while not(split):
    for i, trip in enumerate(new_trips):
        if int(trip["departure_time"].values[-1].split(":")[0]) > 24:
            new_trips.pop(i)
            new1, new2 = [x for _, x in trip.groupby(trip["departure_time"].apply(lambda x: check_hours(x, 24)))]
            
            new2["trip_id"] = new2["trip_id"].map(increment_trip_id, na_action='ignore')
            new2["arrival_time"] = new2["arrival_time"].map(decrease_day, na_action='ignore')
            new2["departure_time"] = new2["departure_time"].map(decrease_day, na_action='ignore')
            new2["stop_sequence"] = [x for x in range(0, new2.shape[0])]
            
            new_trips.append(new1)
            new_trips.append(new2)
            
            split = False
            break
        else:
            split = True
    
print("\nSplit:")
for x in new_trips:
    print(x)