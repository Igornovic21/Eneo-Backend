from rest_framework import serializers

class ActionStatSerializer(serializers.Serializer):
    metric = serializers.CharField(source='record__action__name')
    total = serializers.IntegerField()

class EnterpriseStatSerializer(serializers.Serializer):
    metric = serializers.CharField(source='record__enterprise__name')
    total = serializers.IntegerField()

class CollectorStatSerializer(serializers.Serializer):
    metric = serializers.CharField(source='collector__name')
    total = serializers.IntegerField()