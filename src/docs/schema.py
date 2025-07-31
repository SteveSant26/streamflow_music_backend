from drf_spectacular.extensions import OpenApiAuthenticationExtension


class SupabaseAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = (
        "common.core.authentication.SupabaseAuthentication"  # ← RUTA EXACTA DE TU CLASE
    )
    name = "BearerAuth"  # ← DEBE COINCIDIR con el nombre en SPECTACULAR_SETTINGS

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
