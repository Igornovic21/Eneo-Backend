import json

from rest_framework import serializers

from record.models import Record, Collector, Action, Enterprise

class CollectorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collector
        fields = ["id", "name"]


class ActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Action
        fields = ["id", "name"]


class EnterpriseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enterprise
        fields = ["id", "name"]

class RecordSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    action = ActionSerializer(many=False, read_only=True)
    collector = ActionSerializer(many=False, read_only=True)
    enterprise = ActionSerializer(many=False, read_only=True)
    
    def get_data(self, obj):
        return json.loads(obj.data)

    class Meta:
        model = Record
        fields = ["id", "data", "action", "collector", "enterprise", "date"]