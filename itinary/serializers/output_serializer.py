import json

from rest_framework import serializers

from itinary.models import Itinary, Region

class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ["id", "name", "ona_name"]

class ItinarySerializer(serializers.ModelSerializer):
    metadata = serializers.SerializerMethodField()

    class Meta:
        model = Itinary
        fields = ["name", "metadata"]

    def get_metadata(self, obj):
        return json.loads(obj.metadata)
