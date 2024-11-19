import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True, default=None)
    profile_picture = models.ImageField(upload_to='profile_picture', blank=True, null=True, default=None)
    
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def full_name(self, obj=None) -> str:
        return "{} {}".format(self.last_name, self.first_name)
    
    class Meta:
        ordering = ["last_login"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]
