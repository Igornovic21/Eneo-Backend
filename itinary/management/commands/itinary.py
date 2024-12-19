import os, json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon, MultiPolygon, GEOSGeometry
from django.db import transaction

from itinary.models import Itinary, Region
from region.constants import SRID

class Command(BaseCommand):
    help = 'Load itinaries and region inside the database'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
        
    def handle(self, *args, **kwargs):
        with open(os.path.join(settings.BASE_DIR, 'fixtures/itineraire.geojson'), 'r') as f:
            itinary_data = json.load(f)
        
        success_count = 0
        error_count = 0
        invalid_geometry = 0
        # itinaries = {}
        for index, feature in enumerate(itinary_data['features']):
            properties = feature["properties"]
            try :
                key = "{} - {}".format(properties["REGION"], index) if properties["REPERE"] is None else properties["REPERE"] + " - {}".format(index)
                region = feature["properties"]["REGION"]
                # geometry = feature["geometry"]
                geometry = GEOSGeometry(json.dumps(feature["geometry"]))
                
                if geometry.geom_type == 'Polygon':
                    self.stdout.write(self.style.ERROR("Polygon geometry"))
                    geometry = MultiPolygon(geometry)
                    
                if not geometry.valid:
                    geometry.transform(SRID)
                    geometry = geometry.buffer(0)
                    self.stdout.write(self.style.ERROR("Geometry not valid for itinary: {}".format(key)))
                    invalid_geometry += 1

                # polygons = []
                # if geometry and geometry["type"] in ["Polygon", "MultiPolygon"]:
                #     for coords in geometry['coordinates']:
                #         polygons.append(Polygon(*coords))
                # multi_polygon = MultiPolygon(polygons)

                region, _ = Region.objects.get_or_create(name=region)
                itinary, _ = Itinary.objects.get_or_create(name=key)
                itinary.region = region
                # itinary.boundary = multi_polygon
                itinary.boundary = geometry
                itinary.save()
                success_count += 1

                # if geometry.srid != SRID:
                #     self.stdout.write(self.style.SUCCESS("Itinary {} saved".format(key)))

                # if key in itinaries.keys():
                #     polygons = itinaries[key]["polygons"]
                #     if geometry and geometry["type"] in ["Polygon", "MultiPolygon"]:
                #         for coords in geometry['coordinates']:
                #             polygons.append(Polygon(*coords))
                #         itinaries[key]["polygons"] = polygons
                # else:
                #     polygons = []
                #     itinaries[key] = {"region": "","polygons": []}
                #     if geometry and geometry["type"] in ["Polygon", "MultiPolygon"]:
                #         for coords in geometry['coordinates']:
                #             polygons.append(Polygon(*coords))
                #         itinaries[key]["polygons"] = polygons

                # itinaries[key]["region"] = region
            
            # for key, value in itinaries.items():
            #     multi_polygon = MultiPolygon(value["polygons"])
            #     region, _ = Region.objects.get_or_create(name=value["region"])
            #     itinary, _ = Itinary.objects.get_or_create(name=key)
            #     itinary.region = region
            #     itinary.boundary = multi_polygon
            #     itinary.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR("Error when saving itinary: {}".format(e)))
                error_count += 1
        return self.stdout.write("Itinaries and regions data loaded: success: {}, error: {}, invalid: {}".format(success_count, error_count, invalid_geometry))

# {
#     "bloc": {
#         "region": "",
#         "polygons": []
#     }
# }