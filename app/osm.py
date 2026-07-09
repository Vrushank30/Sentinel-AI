import osmnx as ox
import requests

def get_hospitals(city="Bengaluru, India"):
    tags = {"amenity": "hospital"}
    gdf = ox.features_from_place(city, tags=tags)
    hospitals = []
    for idx, row in gdf.iterrows():
        try:
            lat = row.geometry.centroid.y
            lon = row.geometry.centroid.x
            name = row.get("name", "Unknown Hospital")
            hospitals.append({
                "name": str(name),
                "type": "hospital",
                "latitude": round(lat, 6),
                "longitude": round(lon, 6)
            })
        except:
            continue
    return hospitals[:10]

def get_power_stations(city="Bengaluru, India"):
    tags = {"power": "station"}
    try:
        gdf = ox.features_from_place(city, tags=tags)
        stations = []
        for idx, row in gdf.iterrows():
            try:
                lat = row.geometry.centroid.y
                lon = row.geometry.centroid.x
                name = row.get("name", "Power Station")
                stations.append({
                    "name": str(name),
                    "type": "power_station",
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6)
                })
            except:
                continue
        return stations[:5]
    except:
        return []

def get_water_supply(city="Bengaluru, India"):
    tags = {"man_made": "water_tower"}
    try:
        gdf = ox.features_from_place(city, tags=tags)
        water = []
        for idx, row in gdf.iterrows():
            try:
                lat = row.geometry.centroid.y
                lon = row.geometry.centroid.x
                name = row.get("name", "Water Supply")
                if str(name) == "nan":
                    name = f"Water Supply Point"
                water.append({
                    "name": str(name),
                    "type": "water_supply",
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6)
                })
            except:
                continue
        return water[:5]
    except:
        return []

def get_all_infrastructure(city="Bengaluru, India"):
    print(f"Fetching infrastructure for {city}...")
    hospitals = get_hospitals(city)
    print(f"Found {len(hospitals)} hospitals")
    power = get_power_stations(city)
    print(f"Found {len(power)} power stations")
    water = get_water_supply(city)
    print(f"Found {len(water)} water supply points")
    
    all_nodes = hospitals + power + water
    
    for i, node in enumerate(all_nodes):
        node["id"] = i + 10
    
    return all_nodes