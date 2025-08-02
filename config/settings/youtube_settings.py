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
    "jazz music",
    "blues music",
    "classical music",
    "folk music",
]

# YouTube categories mapping
YOUTUBE_CATEGORIES = {
    1: "Film & Animation",
    2: "Autos & Vehicles",
    10: "Music",
    15: "Pets & Animals",
    17: "Sports",
    18: "Short Movies",
    19: "Travel & Events",
    20: "Gaming",
    21: "Videoblogging",
    22: "People & Blogs",
    23: "Comedy",
    24: "Entertainment",
    25: "News & Politics",
    26: "Howto & Style",
    27: "Education",
    28: "Science & Technology",
    29: "Nonprofits & Activism",
    30: "Movies",
    31: "Anime/Animation",
    32: "Action/Adventure",
    33: "Classics",
    34: "Comedy",
    35: "Documentary",
    36: "Drama",
    37: "Family",
    38: "Foreign",
    39: "Horror",
    40: "Sci-Fi/Fantasy",
    41: "Thriller",
    42: "Shorts",
    43: "Shows",
    44: "Trailers",
}

# yt-dlp configuration for audio extraction
YT_DLP_AUDIO_OPTS = {
    "format": "bestaudio/best",
    "extractaudio": True,
    "audioformat": "mp3",
    "audioquality": "192",
    "quiet": True,
    "no_warnings": True,
    "writesubtitles": False,
    "writeautomaticsub": False,
    "referer": "https://www.youtube.com/",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
