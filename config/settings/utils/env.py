import os
from pathlib import Path

from environ import Env

BASE_DIR = Path(__file__).resolve().parent.parent

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


env = Env()
env_file = BASE_DIR / f".env.{ENVIRONMENT}"
env.read_env(env_file)


__all__ = [
    "env",
    "ENVIRONMENT",
    "BASE_DIR",
]
