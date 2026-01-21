from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return hasattr(obj, "user") and obj.user == request.user