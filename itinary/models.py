import uuid

from django.contrib.gis.db import models

from region.constants import SRID
from region.models import Region

class Itinary(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    name = models.CharField(max_length=100)
    block_code = models.CharField(max_length=100, blank=True, null=True)
    boundary = models.GeometryField(blank=True, null=True, srid=SRID)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, default=None, null=True, blank=True)

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