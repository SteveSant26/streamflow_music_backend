import dj_database_url

from .utils.env import env

DATABASES = {"default": dj_database_url.parse(env("DATABASE_URL"))}
