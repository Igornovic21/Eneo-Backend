import uuid

from django.contrib.gis.db import models

class Region(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    name = models.CharField(max_length=100)
    geojson_file = models.FileField(upload_to="geojson_files/", blank=True, null=True)
    geojson_area = models.MultiPolygonField(blank=True, null=True)
    geojson_content = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]