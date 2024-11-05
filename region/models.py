from django.contrib.gis.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    geojson_file = models.FileField(upload_to="geojson_files/")
    geojson_area = models.MultiPolygonField(blank=True, null=True)
    geojson_content = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name