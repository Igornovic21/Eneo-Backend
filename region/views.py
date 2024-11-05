import json

from django.contrib.gis.geos import Point, MultiPolygon, GEOSGeometry, Polygon
from django.shortcuts import HttpResponse

from region.constants import SRID
from region.models import Location

# Create your views here.
def index(request):
    # point = Point(2.719964, 10.047446, srid=SRID)
    # point.transform(SRID)
    # print(Location.objects.all()[1])
    # area:MultiPolygon = Location.objects.all()[1].geojson_area
    # print(area.contains(point))
    # area_contains = Location.objects.filter(geojson_area__contains=point)
    # if area_contains.exists():
    #     return HttpResponse("contain")
    with open('cmr.geojson', encoding='utf-8') as f:
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
        print(multipolygon.srid)
        # Check if the point is inside the MultiPolygon
        if multipolygon.contains(point):
            # Optional: print feature properties or perform any specific actions
            print(feature['properties'])
            return HttpResponse("The point is inside this geometry!") # Stop if you only need the first matching geometry
        else:
            return HttpResponse("The point is not inside any geometry.")