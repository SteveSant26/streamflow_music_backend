import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from asgiref.sync import async_to_sync

from common.mixins.logging_mixin import LoggingMixin


class SupabaseAuthentication(BaseAuthentication, LoggingMixin):
    """
    Autenticación basada en tokens de Supabase.
    """

    target_class = "common.core.authentication.SupabaseAuthentication"
    name = "BearerAuth"

    def __init__(self):
        self._user_repository = None
        self._sync_user_use_case = None

    def _get_user_repository(self):
        if self._user_repository is None:
            from apps.user_profile.infrastructure.repository import UserRepository

            self._user_repository = UserRepository()
        return self._user_repository

    def _get_sync_user_use_case(self):
        if self._sync_user_use_case is None:
            from apps.user_profile.use_cases import SyncUserFromSupabase

            user_repository = self._get_user_repository()
            self._sync_user_use_case = SyncUserFromSupabase(user_repository)
        return self._sync_user_use_case

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        self.logger.debug(f"Authorization header: {auth_header}")

        if not auth_header or not auth_header.startswith("Bearer "):
            self.logger.warning("No valid Authorization header found.")
            return None

        token = auth_header.split("Bearer ")[1]
        self.logger.debug(f"Extracted token: {token}")

        try:
            decoded = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=settings.SUPABASE_JWT_ALGORITHM,
                options={"verify_aud": False},
            )

            self.logger.debug(f"Decoded token: {decoded}")

            sync_user = self._get_sync_user_use_case()
            user_entity = sync_user.execute(decoded)

            # Llamar la función async desde sync
            user_repository = self._get_user_repository()
            user = async_to_sync(user_repository.get_by_id)(user_entity.id)

            if not user:
                self.logger.error("User not found after syncing from Supabase.")
                raise AuthenticationFailed("User not found.")

            self.logger.info(f"Authenticated user: {user.email}")
            return (user, token)

        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationFailed(f"Invalid Supabase token: {str(e)}")
