import uuid

from django.utils import timezone
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point

from itinary.models import Itinary
from region.constants import SRID

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
    matricule = models.CharField(max_length=100, default="")

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


class Record(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    ona_id = models.CharField(max_length=100, editable=False, unique=True, db_index=True)

    contrat = models.CharField(max_length=250, default="", db_index=True)
    amount = models.CharField(max_length=250, default="", db_index=True)
    accessibility = models.CharField(max_length=250, default="", db_index=True)
    code_anomaly = models.CharField(max_length=250, default="", db_index=True)
    sealed_number = models.CharField(max_length=250, default="", db_index=True)
    cut_action = models.CharField(max_length=250, default="", db_index=True)
    delivery_points = models.PositiveIntegerField(default=0, db_index=True)
    source = models.CharField(max_length=250, default="", db_index=True)
    poste = models.CharField(max_length=250, default="", db_index=True)
    depart = models.CharField(max_length=250, default="", db_index=True)
    depart_nbr = models.CharField(max_length=250, default="", db_index=True)
    depart_code = models.CharField(max_length=250, default="", db_index=True)
    poste_type = models.CharField(max_length=250, default="", db_index=True)
    existence = models.CharField(max_length=250, default="", db_index=True)
    telephone = models.CharField(max_length=250, default="", db_index=True)
    quality = models.CharField(max_length=250, default="", db_index=True)
    lighting = models.CharField(max_length=250, default="", db_index=True)
    poste_image_url = models.CharField(max_length=250, default="", db_index=True)
    i1_input = models.CharField(max_length=250, default="", db_index=True)
    i1_output = models.CharField(max_length=250, default="", db_index=True)
    i2_input = models.CharField(max_length=250, default="", db_index=True)
    i2_output = models.CharField(max_length=250, default="", db_index=True)
    i3_input = models.CharField(max_length=250, default="", db_index=True)
    i3_output = models.CharField(max_length=250, default="", db_index=True)
    i4_input = models.CharField(max_length=250, default="", db_index=True)
    i4_output = models.CharField(max_length=250, default="", db_index=True)
    banoc_code = models.CharField(max_length=250, default="", db_index=True)

    action = models.ForeignKey(Action, on_delete=models.DO_NOTHING, null=True, blank=True, db_index=True)
    collector = models.ForeignKey(Collector, on_delete=models.DO_NOTHING, null=True, blank=True, db_index=True)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.DO_NOTHING, null=True, blank=True, db_index=True)
    itinary = models.ForeignKey(Itinary, on_delete=models.DO_NOTHING, default=None, null=True, blank=True, related_name="records", db_index=True)
    date = models.DateTimeField(default=timezone.now, db_index=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        if self.itinary is None:
            return self.ona_id
        return self.ona_id + " " + self.itinary.name

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['itinary']),
            models.Index(fields=['ona_id']),
            models.Index(fields=['action']),
            models.Index(fields=['collector']),
            models.Index(fields=['enterprise']),
            models.Index(fields=['contrat']),
            models.Index(fields=['amount']),
            models.Index(fields=['accessibility']),
            models.Index(fields=['code_anomaly']),
            models.Index(fields=['sealed_number']),
            models.Index(fields=['cut_action']),
            models.Index(fields=['delivery_points']),
        ]


class Location(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    coordinates = gis_models.PointField(geography=False, srid=SRID)
    record = models.OneToOneField(Record, on_delete=models.CASCADE, null=True, blank=True, db_index=True, related_name="location")
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "Location for {}".format(self.record.ona_id)
    
    class Meta:
        indexes = [
            models.Index(fields=["record"]),
            models.Index(fields=["coordinates"]),
        ]


class DeliveryPoint(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    type = models.CharField(max_length=250, default="", db_index=True)
    reason = models.CharField(max_length=250, default="", db_index=True)
    status = models.CharField(max_length=250, default="", db_index=True)
    activite = models.CharField(max_length=250, default="", db_index=True)
    batiment = models.CharField(max_length=250, default="", db_index=True)
    index = models.CharField(max_length=250, default="", db_index=True)
    contrat = models.CharField(max_length=250, default="", db_index=True)
    code_bare = models.CharField(max_length=250, default="", db_index=True)
    thread_nbr = models.CharField(max_length=250, default="", db_index=True)
    serial_number = models.CharField(max_length=250, default="", db_index=True)
    image_url = models.CharField(max_length=250, default=None, null=True, blank=True, db_index=True)
    record = models.ForeignKey(Record, on_delete=models.CASCADE, null=True, blank=True, db_index=True, related_name="pl")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.type + " " + self.record.ona_id

    class Meta:
        ordering = ['-date_updated']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['status']),
            models.Index(fields=['activite']),
            models.Index(fields=['batiment']),
            models.Index(fields=['code_bare']),
            models.Index(fields=['image_url']),
            models.Index(fields=['serial_number']),
            models.Index(fields=['record']),
        ]
