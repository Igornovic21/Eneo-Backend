import uuid

from django.contrib.gis.db import models

from user.models import User

class Region(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    name = models.CharField(max_length=100, unique=True)
    ona_name = models.CharField(max_length=100, blank=True,null=True)
    supervisor = models.ManyToManyField(User, default=None, blank=True, related_name="region")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['ona_name']),
        ]