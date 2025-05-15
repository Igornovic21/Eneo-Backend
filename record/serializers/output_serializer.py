import json

from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

from record.models import Record, Collector, Action, Enterprise, DeliveryPoint, Location

from itinary.serializers.output_serializer import ItinarySerializer

class CollectorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collector
        fields = ["id", "name", "matricule"]


class ActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Action
        fields = ["id", "name"]


class DeliveryPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryPoint
        fields = ["type", "index", "status", "activite", "batiment", "code_bare", "serial_number", "reason", "image_url"]


class LocationSerializer(gis_serializers.GeoFeatureModelSerializer):

    class Meta:
        model = Location
        geo_field = "coordinates"
        fields = ["coordinates"]

    def to_representation(self, instance):
        coordinates = instance.coordinates

        if coordinates:
            return [coordinates.x, coordinates.y]
        return None


class EnterpriseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enterprise
        fields = ["id", "name"]

class RecordSerializer(serializers.ModelSerializer):
    # action = ActionSerializer(many=False, read_only=True)
    # collector = ActionSerializer(many=False, read_only=True)
    # enterprise = ActionSerializer(many=False, read_only=True)
    itinary = ItinarySerializer(many=False, read_only=True)
    location = LocationSerializer(many=False, read_only=True)
    pl = DeliveryPointSerializer(many=True, read_only=True)
    action = serializers.SerializerMethodField()
    collector = serializers.SerializerMethodField()
    enterprise = serializers.SerializerMethodField()

    class Meta:
        model = Record
        fields = ["id", "ona_id", "contrat", "amount", "accessibility", "code_anomaly", "sealed_number", "cut_action", "delivery_points", "itinary", "action", "collector", "enterprise", "date", "location", "pl", "itinary"]

    def get_action(self, obj):
        return obj.action.name if obj.action else None
    
    def get_collector(self, obj):
        return obj.collector.name if obj.collector else None
    
    def get_enterprise(self, obj):
        return obj.enterprise.name if obj.enterprise else None