
from django.urls import path

from region import views

urlpatterns = [
    path("", views.index, name="index")
]