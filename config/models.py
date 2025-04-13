import uuid

from django.db import models

from user.models import User

# Create your models here.
class Credential(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    ona_token = models.CharField()
    fields = models.TextField()

    def __str__(self) -> str:
        return "API CONFIG"


class OdkPosition(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    project_id = models.PositiveIntegerField(default=0)
    form_name = models.CharField(max_length=10, default="")
    file = models.FileField()
    uploaded_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=None, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "{} by {}".format(self.form_name, self.uploaded_by.email)