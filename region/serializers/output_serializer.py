from rest_framework import serializers

class RegionSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    records = serializers.IntegerField()