import requests, json

from django.contrib.gis.geos import Point, MultiPolygon, GEOSGeometry, Polygon

from region.constants import SRID

headers = {
    "Authorization": "Token a8996c762270c9104b53f42d50061028c22d4896"
}

def get_project() -> list[dict]:
    response = requests.get("https://api.ona.io/api/v1/projects", headers=headers)
    if response.status_code != 200:
        print("error when getting projects")
    
    for project in response.json():
        if project["name"] == "COLLECTE DES PL (AV)":
            return project["forms"]

def get_form_data(forms: list[dict]):
    for form in forms:
        print(form["formid"])

def check_point():
    with open('path/to/your/geojson_file.geojson') as f:
        geojson_data = json.load(f)

    point = Point(2.719964, 10.047446, srid=SRID)

    for feature in geojson_data['features']:
        geometry = feature['geometry']
        
        # Convert the geometry to a MultiPolygon if it’s not already
        if geometry['type'] == 'MultiPolygon':
            multipolygon = GEOSGeometry(json.dumps(geometry))
        elif geometry['type'] == 'Polygon':
            multipolygon = MultiPolygon(Polygon(*geometry['coordinates']))
        else:
            pass  # Skip if not a Polygon or MultiPolygon

        # Check if the point is inside the MultiPolygon
        if multipolygon.contains(point):
            print("The point is inside this geometry!")
            # Optional: print feature properties or perform any specific actions
            print(feature['properties'])
            return # Stop if you only need the first matching geometry
        else:
            print("The point is not inside any geometry.")

if __name__ == "__main__":
    # forms = get_project()
    # get_form_data(forms)
    check_point()