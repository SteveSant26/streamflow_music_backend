import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class SupabaseAuthentication(BaseAuthentication):
    """
    Autenticación basada en tokens de Supabase.

    Esta implementación sigue principios de arquitectura limpia al no depender
    directamente de casos de uso o repositorios. En su lugar, estos se deben
    inyectar o configurar a través de un factory pattern o service locator.
    """

    target_class = "common.core.authentication.SupabaseAuthentication"  # Ruta exacta
    name = "BearerAuth"

    def __init__(self):
        # Lazy imports para evitar dependencias circulares y violaciones de jerarquía
        self._user_repository = None
        self._sync_user_use_case = None

    def _get_user_repository(self):
        """Lazy loading del repositorio de usuarios."""
        if self._user_repository is None:
            from apps.user_profile.infrastructure.repository import UserRepository

            self._user_repository = UserRepository()
        return self._user_repository

    def _get_sync_user_use_case(self):
        """Lazy loading del caso de uso de sincronización."""
        if self._sync_user_use_case is None:
            from apps.user_profile.use_cases import SyncUserFromSupabase

            user_repository = self._get_user_repository()
            self._sync_user_use_case = SyncUserFromSupabase(user_repository)
        return self._sync_user_use_case

    async def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        logger.debug(f"Authorization header: {auth_header}")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("No valid Authorization header found.")
            return None

        token = auth_header.split("Bearer ")[1]
        logger.debug(f"Extracted token: {token}")

        try:
            # Decodifica el token con HS256 y la clave secreta
            decoded = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=settings.SUPABASE_JWT_ALGORITHM,
                options={"verify_aud": False},
            )

            logger.debug(f"Decoded token: {decoded}")

            # Usar lazy loading para obtener dependencias
            user_repository = self._get_user_repository()
            sync_user = self._get_sync_user_use_case()

            user_entity = sync_user.execute(decoded)
            user = await user_repository.get_by_id(user_entity.id)
            if not user:
                logger.error("User not found after syncing from Supabase.")
                raise AuthenticationFailed("User not found.")

            logger.info(f"Authenticated user: {user.email}")

            return (user, token)

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationFailed(f"Invalid Supabase token: {str(e)}")
