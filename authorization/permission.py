from django.utils.translation import gettext as _

from rest_framework.permissions import BasePermission

class IsActiveAccount(BasePermission):
    def has_permission(self, request, view):
        message = _("Your account has not yet been verified.")
        return bool(request.user and request.user.is_authenticated and request.user.is_active)
        
class IsOwnerAccount(BasePermission):
    message = _("You do not have permission to perform this action.")
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == "Owner")
