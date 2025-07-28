import dj_database_url

from .utils.env import env

database_url = env("DATABASE_URL")
if not isinstance(database_url, str) or not database_url:
    raise ValueError(
        "DATABASE_URL environment variable must be set and must be a string."
    )
DATABASES = {"default": dj_database_url.parse(database_url)}
