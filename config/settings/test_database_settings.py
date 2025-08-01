"""
Configuración de base de datos para testing
"""

import sys
import config.settings.database_settings as db_settings  # Ajusta el path según tu estructura

# Si estamos ejecutando tests, usar SQLite en memoria
if "test" in sys.argv or "pytest" in sys.modules:
    db_settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "OPTIONS": {
            "timeout": 20,
        },
    }
    print("🧪 Usando SQLite en memoria para tests")
