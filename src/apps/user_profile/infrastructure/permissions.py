from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsPlaylistOwner(BasePermission):
    """
    Permiso específico para playlists que verifica si el usuario
    es el propietario de la playlist.
    """

    def has_object_permission(self, request, view, obj) -> Any:
        # Verificar si el usuario está autenticado
        if (
            not request.user
            or not hasattr(request.user, "is_authenticated")
            or not request.user.is_authenticated
        ):
            return False

        # Para modelos de playlist
        if hasattr(obj, "user"):
            user = getattr(obj, "user", None)
            if user is not None:
                if hasattr(user, "id"):
                    return str(user.id) == str(request.user.id)
                else:
                    return str(user) == str(request.user.id)

        # Para entidades de playlist del dominio
        elif hasattr(obj, "user_id"):
            user_id = getattr(obj, "user_id", None)
            if user_id is not None:
                return str(user_id) == str(request.user.id)

        return False


class IsPlaylistOwnerOrPublic(BasePermission):
    """
    Permiso específico para playlists que permite:
    - Acceso completo al propietario
    - Solo lectura para playlists públicas
    """

    def has_object_permission(self, request, view, obj) -> Any:
        # Verificar si es una playlist pública y es una operación de lectura
        if request.method in SAFE_METHODS:
            is_public = getattr(obj, "is_public", False)
            if is_public:
                return True

        # Verificar si es el propietario
        playlist_owner_permission = IsPlaylistOwner()
        return playlist_owner_permission.has_object_permission(request, view, obj)
