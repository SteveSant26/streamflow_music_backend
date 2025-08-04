import sys

import dj_database_url

from .utils.env import env

database_test = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
    "OPTIONS": {
        "timeout": 20,
    },
}

# Detectar si se está ejecutando en modo test
is_testing = len(sys.argv) > 1 and sys.argv[1] == "test"

if is_testing:
    DATABASES = {"default": database_test}
else:
    database_url = env("DATABASE_URL")
    if not isinstance(database_url, str) or not database_url:
        raise ValueError(
            "DATABASE_URL environment variable must be set and must be a string."
        )
    DATABASES = {"default": dj_database_url.parse(database_url)}
