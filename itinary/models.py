import uuid

from django.contrib.gis.db import models

from region.models import Region

class Itinary(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    name = models.CharField(max_length=100, unique=True)
    boundary = models.MultiPolygonField(blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['region']),
            models.Index(fields=['boundary']),
        ]