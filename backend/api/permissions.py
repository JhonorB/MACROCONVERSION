from rest_framework import permissions

class IsAuthenticated(permissions.IsAuthenticated):
    pass

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'perfil') and 
            request.user.perfil.rol == 'ADMIN'
        )

class IsContador(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'perfil') and 
            request.user.perfil.rol == 'CONTADOR'
        )

class IsAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'ADMIN':
            return True
        return getattr(obj, 'usuario', None) == request.user
