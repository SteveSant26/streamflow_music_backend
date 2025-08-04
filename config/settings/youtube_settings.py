import json
import os
from typing import List

from .utils.env import env

YOUTUBE_API_KEY = env("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY must be set in the environment variables")
YOUTUBE_API_SERVICE_NAME = os.getenv("YOUTUBE_API_SERVICE_NAME", "youtube")
YOUTUBE_API_VERSION = os.getenv("YOUTUBE_API_VERSION", "v3")

# Random search queries for the random songs endpoint
RANDOM_MUSIC_QUERIES: List[str] = [
    "kpop 2024",
    "reggaeton",
    "pop music",
    "hip hop",
    "trap music",
    "rock music",
    "electronic music",
    "latin music",
    "indie music",
    "r&b music",
    "country music",
]


with open("./config/settings/music_genres.json", "r", encoding="utf-8") as f:
    YOUTUBE_MUSIC_GENRES = json.load(f)
