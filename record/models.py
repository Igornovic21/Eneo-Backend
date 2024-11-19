import uuid

from django.utils import timezone
from django.db import models

from config.models import FormData

# Create your models here.
class Record(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    form = models.ForeignKey(FormData, on_delete=models.DO_NOTHING, null=True, blank=True)
    ona_id = models.CharField(max_length=100, editable=False, unique=True)
    data = models.TextField()
    full_data = models.TextField()
    action = models.CharField(max_length=100)
    collector = models.CharField(max_length=100)
    enterprise = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.form.region.name + " Record"
    
    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['form']),
            models.Index(fields=['ona_id']),
            models.Index(fields=['action']),
            models.Index(fields=['collector']),
            models.Index(fields=['enterprise']),
            models.Index(fields=['date']),
        ]