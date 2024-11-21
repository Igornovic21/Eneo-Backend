import json

from django.core.management.base import BaseCommand
# from django.contrib.gis.geos import Point

from shapely.geometry import shape, Point

# from itinary.models import Itinary

class Command(BaseCommand):
    help = 'Update all record date'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
        
    def handle(self, *args, **kwargs): 
        latitude = 4.1536513
        longitude = 9.2855841

        with open('DRSOM.geojson', 'r') as f:
            geojson_data = json.load(f)
    
        point = Point(longitude, latitude)

        for feature in geojson_data['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                return print("The point is inside the GeoJSON area.")
            print("The point is outside the GeoJSON area.")

        # results = Itinary.objects.only("boundary").filter(boundary__contains=point)
        # print(results)