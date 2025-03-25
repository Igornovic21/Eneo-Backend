# from rest_framework import serializers

# from property.models import Property, Location, Asset, Pricing

# class AdminUpdatePropertySerialiser(serializers.Serializer):
#     status = serializers.CharField()
#     topic = serializers.CharField(required=False, allow_blank=True)
#     message = serializers.CharField(required=False, allow_blank=True)

# class RegisterPropertySerialiser(serializers.ModelSerializer):
    
#     class Meta:
#         model = Property
#         fields = ["id", "name", "description", "type", "cover", "bedrooms", "bathrooms", "restrooms", "kitchens"]
