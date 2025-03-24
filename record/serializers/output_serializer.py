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
        fields = ["type", "status", "activite", "batiment", "code_bare", "serial_number", "image_url"]


class LocationSerializer(gis_serializers.GeoFeatureModelSerializer):

    class Meta:
        model = Location
        geo_field = "coordinates"
        fields = ["coordinates"]

    def to_representation(self, instance):
        coordinates = instance.coordinates

        if coordinates:
            return {
                'coordinates': [coordinates.y, coordinates.x]
            }
        return {
            'coordinates': None
        }


class EnterpriseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enterprise
        fields = ["id", "name"]

class RecordSerializer(serializers.ModelSerializer):
    # action = ActionSerializer(many=False, read_only=True)
    # collector = ActionSerializer(many=False, read_only=True)
    # enterprise = ActionSerializer(many=False, read_only=True)
    # itinary = ItinarySerializer(many=False, read_only=True)
    location = LocationSerializer(many=False, read_only=True)
    pl = DeliveryPointSerializer(many=True, read_only=True)

    class Meta:
        model = Record
        fields = ["id", "ona_id", "contrat", "amount", "accessibility", "code_anomaly", "sealed_number", "cut_action", "delivery_points", "action", "collector", "enterprise", "date", "location", "pl"]
