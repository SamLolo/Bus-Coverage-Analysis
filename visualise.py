import geopandas as gpd

bus = gpd.read_file("out/exeter_bus.gpkg")
car = gpd.read_file("out/exeter_car.gpkg")

map = bus.explore(column="travel_time", colour="red")
map = car.explore(column="travel_time", colour="green", m=map)
map.save("out/exeter.html")