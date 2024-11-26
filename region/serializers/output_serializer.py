from rest_framework import serializers

from region.models import Region

class RegionSerializer(serializers.ModelSerializer):
    records = serializers.IntegerField()

    class Meta:
        model = Region
        fields = ["id", "name", "ona_name", "records"]