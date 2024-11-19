import json

from rest_framework import serializers

from record.models import Record

class RecordSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    
    def get_data(self, obj):
        return json.loads(obj.data)

    class Meta:
        model = Record
        fields = ["id", "data", "action", "collector", "enterprise", "date"]