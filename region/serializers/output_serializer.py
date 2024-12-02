from rest_framework import serializers

from region.models import Region

class RegionStatSerializer(serializers.ModelSerializer):
    records = serializers.IntegerField()

    class Meta:
        model = Region
        fields = ["id", "name", "ona_name", "records"]


class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ["id", "name", "ona_name"]