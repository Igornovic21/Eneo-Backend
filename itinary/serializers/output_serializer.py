import json

from rest_framework import serializers

from itinary.models import Itinary, Region

class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ["id", "name", "ona_name"]

class ItinarySerializer(serializers.ModelSerializer):
    metadata = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    region = RegionSerializer(many=False, read_only=True)
    
    class Meta:
        model = Itinary
        fields = ["id", "name", "metadata", "region", "block_code", "records"]

    def get_metadata(self, obj):
        return json.loads(obj.metadata)

    def get_records(self, obj):
        return obj.records.count()