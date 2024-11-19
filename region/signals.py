import json

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.db import models
from django.dispatch import receiver

from region.constants import SRID
from region.models import Region

@receiver(models.signals.post_save, sender=Region)
def get_geo_content(sender, instance, **kwargs):
    if instance.geojson_file:
        print("============= open geojson file ===============")
        with instance.geojson_file.open() as f:
            geojson_data = f.read().decode("utf-8")

        if isinstance(geojson_data, dict):
            geojson_data = json.dumps(geojson_data)

        geojson_dict = json.loads(geojson_data)
        
        if geojson_dict.get("type") == "FeatureCollection":
            polygons = []
            for feature in geojson_dict.get("features", []):
                geometry = feature.get("geometry")
                if geometry and geometry["type"] in ["Polygon", "MultiPolygon"]:
                    # geom = GEOSGeometry(json.dumps(geometry), srid=SRID)
                    for coords in geometry['coordinates']:
                        polygon = Polygon(*coords)
                        polygons.append(polygon)
                    # polygons.append(geom) 
                    

            if polygons:
                multi_polygon = MultiPolygon(polygons)
                # instance.geojson_area = multi_polygon
                Region.objects.filter(id=instance.id).update(geojson_area=multi_polygon, geojson_content=geojson_data)
                # instance.save()
                return

        if geojson_dict.get("type") in ["Polygon", "MultiPolygon"]:
            geometry = GEOSGeometry(geojson_data, srid=SRID)
            if geometry.geom_type in ['Polygon', 'MultiPolygon']:
                # instance.geojson_area = geometry
                Region.objects.filter(id=instance.id).update(geojson_area=geometry, geojson_content=geojson_data)
            # instance.geojson_content = geojson_data
            # instance.save()