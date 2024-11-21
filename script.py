import os, json

from shapely.geometry import shape, Point

# 4.5754986, 13.7016681 Inside
# 6.179836, 39.283501 Not Inside

itinary_file = 'itineraire.geojson'
geojson_file = 'DRSOM.geojson'
latitude = 4.1536513
longitude = 9.2855841

# 4.1536513
# 9.2855841

def load_geojson(file_path):
    with open(file_path, 'r') as f:
        geojson_data = json.load(f)
    return geojson_data

def is_point_inside_geojson(geojson_file, lat, lon):
    geojson_data = load_geojson(geojson_file)

    # Create a point from the provided coordinates
    point = Point(lon, lat)  # Note: GeoJSON uses [longitude, latitude]

    # Iterate through each feature in the GeoJSON
    for feature in geojson_data['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return True
    return False


if __name__ == "__main__":
    if is_point_inside_geojson(geojson_file, latitude, longitude):
        print("The point is inside the GeoJSON area.")
    else:
        print("The point is outside the GeoJSON area.")