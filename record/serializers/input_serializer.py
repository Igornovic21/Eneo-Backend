from rest_framework import serializers

from record.models import Record

# class AdminUpdatePropertySerialiser(serializers.Serializer):
#     status = serializers.CharField()
#     topic = serializers.CharField(required=False, allow_blank=True)
#     message = serializers.CharField(required=False, allow_blank=True)

class UpdateRecordSerialiser(serializers.ModelSerializer):
    
    class Meta:
        model = Record
        fields = ["banoc_code"]
