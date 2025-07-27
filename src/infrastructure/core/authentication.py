import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import PyJWKClient
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SupabaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split("Bearer ")[1]

        try:
            # Obtén la JWK desde Supabase
            jwks_url = (
                f"https://{settings.SUPABASE_PROJECT_ID}.supabase.co/auth/v1/keys"
            )
            jwk_client = PyJWKClient(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)

            # Decodifica el token
            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=None,
                options={"verify_aud": False},
            )

            # Buscar o crear el usuario localmente
            user_model = get_user_model()
            user, _ = user_model.objects.get_or_create(email=decoded["email"])
            return (user, token)

        except Exception as e:
            raise AuthenticationFailed(f"Invalid Supabase token: {str(e)}")
