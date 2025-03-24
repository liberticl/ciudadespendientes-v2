from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps
from .models import StravaData
from django.db.models import Prefetch


def user_has_zone_permission(view_func):
    """
        Verifica que el usuario tenga permiso de visualización
        de zonas específicas.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        user_zones = request.user.zones.prefetch_related(
            Prefetch('sectores', queryset=StravaData.objects.all())
        ).all()
        user_sectors = StravaData.objects.filter(
            sectores__in=user_zones).distinct()
        sectors = user_sectors.values_list('sector', flat=True).distinct()

        if not sectors:
            raise PermissionDenied(
                "No tienes zonas de visualización asignadas.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def user_has_permission(permissions):
    """
        Verifica que el usuario tenga los permisos requeridos
        para ver un contenido específico
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            can_view = all(request.user.has_permission(
                perm) for perm in permissions)

            if not can_view:
                raise PermissionDenied(
                    "No tienes permisos para ver este contenido.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
