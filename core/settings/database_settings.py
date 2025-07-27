from pathlib import Path

import dj_database_url

from .base import env

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {"default": dj_database_url.parse(env("DATABASE_URL"))}
