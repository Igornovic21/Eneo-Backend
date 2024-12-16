import uuid

from django.utils import timezone
from django.db import models
from django.db.models import Func, Index

from itinary.models import Itinary

# Create your models here.
class Action(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    name = models.CharField(max_length=100)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ['date_created']
        indexes = [
            models.Index(fields=['name']),
        ]


class Collector(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    name = models.CharField(max_length=100)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ['date_created']
        indexes = [
            models.Index(fields=['name']),
        ]


class Enterprise(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    
    name = models.CharField(max_length=100)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ['date_created']
        indexes = [
            models.Index(fields=['name']),
        ]


# class Pl(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

#     type = models.CharField(max_length=100, default="")
#     status = models.CharField(max_length=100, default="")
#     serial_number = models.CharField(max_length=100, default="")

#     date_created = models.DateTimeField(auto_now_add=True)
#     date_updated = models.DateTimeField(auto_now=True)
    
#     def __str__(self) -> str:
#         return self.serial_number


class Record(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    itinary = models.ForeignKey(Itinary, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="records")
    ona_id = models.CharField(max_length=100, editable=False, unique=True)
    data = models.TextField()
    full_data = models.TextField()
    action = models.ForeignKey(Action, on_delete=models.DO_NOTHING, null=True, blank=True)
    collector = models.ForeignKey(Collector, on_delete=models.DO_NOTHING, null=True, blank=True)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.DO_NOTHING, null=True, blank=True)
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