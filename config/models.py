import uuid

from django.db import models

from region.models import Region

# Create your models here.
class Credential(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    ona_token = models.CharField()

    def __str__(self) -> str:
        return "API TOKEN"

class FormData(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    region = models.OneToOneField(Region, on_delete=models.DO_NOTHING, null=True, blank=True)
    fields = models.TextField()

    def __str__(self) -> str:
        return self.region.name + " Form"

    class Meta:
        indexes = [
            models.Index(fields=['region']),
        ]