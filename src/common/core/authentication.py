import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.user_profile.infrastructure.models import UserProfileModel
from apps.user_profile.infrastructure.repository import UserRepository
from apps.user_profile.use_cases import SyncUserFromSupabase
from src.common.utils import get_logger

logger = get_logger(__name__)


class SupabaseAuthentication(BaseAuthentication):
    target_class = "common.core.authentication.SupabaseAuthentication"  # Ruta exacta
    name = "BearerAuth"

    def authenticate(self, request):
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

            sync_user = SyncUserFromSupabase(UserRepository())
            user_entity = sync_user.execute(decoded)
            user = UserProfileModel.objects.get(email=user_entity.email)

            logger.info(f"Authenticated user: {user.email}")

            return (user, token)

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationFailed(f"Invalid Supabase token: {str(e)}")
