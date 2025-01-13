from rest_framework import serializers


from user.models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "last_login", "username", "email", "first_name", "last_name", "is_superuser", "date_joined"]
