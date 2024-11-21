import os, json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon, MultiPolygon, GEOSGeometry

from itinary.models import Itinary, Region

class Command(BaseCommand):
    help = 'Load itinaries and region inside the database'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
        
    def handle(self, *args, **kwargs):
        with open(os.path.join(settings.BASE_DIR, 'fixtures/itineraire.geojson'), 'r') as f:
            itinary_data = json.load(f)
        
        itinaries = {}
        for feature in itinary_data['features']:
            key = "No Name {}".format(feature["properties"]["REGION"]) if feature["properties"]["LOCALITE"] is None else feature["properties"]["LOCALITE"]
            region = feature["properties"]["REGION"]
            geometry = feature["geometry"]
            polygons = []

            if key in itinaries.keys():
                polygons = itinaries[key]["polygons"]
                if geometry and geometry["type"] in ["Polygon", "MultiPolygon"]:
                    for coords in geometry['coordinates']:
                        polygons.append(Polygon(*coords))
                    itinaries[key]["polygons"] = polygons
            else:
                polygons = []
                itinaries[key] = {"region": "","polygons": []}
                if geometry and geometry["type"] in ["Polygon", "MultiPolygon"]:
                    for coords in geometry['coordinates']:
                        polygons.append(Polygon(*coords))
                    itinaries[key]["polygons"] = polygons

            itinaries[key]["region"] = region
        
        for key, value in itinaries.items():
            multi_polygon = MultiPolygon(value["polygons"])
            region, _ = Region.objects.get_or_create(name=value["region"])
            itinary, _ = Itinary.objects.get_or_create(name=key)
            itinary.region = region
            itinary.boundary = multi_polygon
            itinary.save()

        return self.stdout.write("Itinaries and regions data loaded")

# {
#     "bloc": {
#         "region": "",
#         "polygons": []
#     }
# }