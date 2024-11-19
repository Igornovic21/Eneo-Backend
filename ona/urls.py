"""
URL configuration for ona project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from user.views import AuthViewSet
from region.views import RegionViewSet, RegionFilterSet
from record.views import RecordViewSet

from rest_framework import routers

routers = routers.DefaultRouter()

routers.register('auth', AuthViewSet, basename='auth')
routers.register('region', RegionViewSet, basename='region')
routers.register('region-filter', RegionFilterSet, basename='region-filter')
routers.register('record', RecordViewSet, basename='record')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(routers.urls)),
]
