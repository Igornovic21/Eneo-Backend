import uuid

from django.utils import timezone
from django.db import models

from itinary.models import Itinary

# Create your models here.
class Record(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    itinary = models.ForeignKey(Itinary, on_delete=models.DO_NOTHING, null=True, blank=True)
    ona_id = models.CharField(max_length=100, editable=False, unique=True)
    data = models.TextField()
    full_data = models.TextField()
    action = models.CharField(max_length=100)
    collector = models.CharField(max_length=100)
    enterprise = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        if self.itinary is None:
            return self.ona_id
        return self.ona_id + " " + self.itinary.name
    
    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['itinary']),
            models.Index(fields=['ona_id']),
            models.Index(fields=['action']),
            models.Index(fields=['collector']),
            models.Index(fields=['enterprise']),
            models.Index(fields=['date']),
        ]