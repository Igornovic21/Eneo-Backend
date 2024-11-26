from rest_framework import serializers

from itinary.models import Itinary, Region

class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ["id", "name", "ona_name"]

class ItinarySerializer(serializers.ModelSerializer):
    region = RegionSerializer(many=False, read_only=True)
    
    class Meta:
        model = Itinary
        fields = ["id", "name", "region"]