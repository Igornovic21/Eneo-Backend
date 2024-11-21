import uuid

from django.db import models

from region.models import Region

# Create your models here.
class Credential(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    ona_token = models.CharField()
    fields = models.TextField()

    def __str__(self) -> str:
        return "API CONFIG"
