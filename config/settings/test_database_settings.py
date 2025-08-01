"""
Configuración de base de datos para testing
"""
import sys


# Si estamos ejecutando tests, usar SQLite en memoria
if "test" in sys.argv or "pytest" in sys.modules:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "OPTIONS": {
                "timeout": 20,
            },
        }
    }
    print("🧪 Usando SQLite en memoria para tests")
else:
    # Usar la configuración normal para desarrollo/producción
    pass
