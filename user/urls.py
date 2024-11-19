from django.urls import path

from user.activate import activate, reset_password

urlpatterns = [
    path('auth/activate/<str:uidb64>/<str:token>/', activate, name='activate'),
    path('auth/reset_password/<str:uidb64>/<str:token>/', reset_password, name='reset-password'),
]
