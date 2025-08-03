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


YOUTUBE_MUSIC_GENRES = {
    # Pop and Mainstream
    "pop": {
        "name": "Pop",
        "category": "Pop",
        "keywords": ["pop", "mainstream", "chart"],
    },
    "kpop": {
        "name": "K-Pop",
        "category": "Pop",
        "keywords": ["kpop", "korean pop", "k-pop"],
    },
    "jpop": {
        "name": "J-Pop",
        "category": "Pop",
        "keywords": ["jpop", "japanese pop", "j-pop"],
    },
    "dance_pop": {
        "name": "Dance Pop",
        "category": "Pop",
        "keywords": ["dance pop", "dance", "upbeat"],
    },
    # Rock and Metal
    "rock": {
        "name": "Rock",
        "category": "Rock",
        "keywords": ["rock", "guitar", "band"],
    },
    "alternative": {
        "name": "Alternative Rock",
        "category": "Rock",
        "keywords": ["alternative", "alt rock", "indie rock"],
    },
    "punk": {
        "name": "Punk",
        "category": "Rock",
        "keywords": ["punk", "punk rock", "hardcore"],
    },
    "metal": {
        "name": "Metal",
        "category": "Rock",
        "keywords": ["metal", "heavy metal", "metalcore"],
    },
    "hard_rock": {
        "name": "Hard Rock",
        "category": "Rock",
        "keywords": ["hard rock", "classic rock"],
    },
    "progressive": {
        "name": "Progressive Rock",
        "category": "Rock",
        "keywords": ["progressive", "prog rock"],
    },
    "grunge": {
        "name": "Grunge",
        "category": "Rock",
        "keywords": ["grunge", "90s rock", "seattle"],
    },
    # Electronic and Dance
    "electronic": {
        "name": "Electronic",
        "category": "Electronic",
        "keywords": ["electronic", "synth", "digital"],
    },
    "edm": {
        "name": "EDM",
        "category": "Electronic",
        "keywords": ["edm", "festival", "rave"],
    },
    "house": {
        "name": "House",
        "category": "Electronic",
        "keywords": ["house", "deep house", "tech house"],
    },
    "techno": {
        "name": "Techno",
        "category": "Electronic",
        "keywords": ["techno", "minimal", "detroit"],
    },
    "trance": {
        "name": "Trance",
        "category": "Electronic",
        "keywords": ["trance", "uplifting", "progressive trance"],
    },
    "dubstep": {
        "name": "Dubstep",
        "category": "Electronic",
        "keywords": ["dubstep", "bass", "wobble"],
    },
    "ambient": {
        "name": "Ambient",
        "category": "Electronic",
        "keywords": ["ambient", "atmospheric", "chill"],
    },
    "synthwave": {
        "name": "Synthwave",
        "category": "Electronic",
        "keywords": ["synthwave", "retrowave", "80s"],
    },
    # Hip Hop and Rap
    "hip_hop": {
        "name": "Hip Hop",
        "category": "Hip Hop",
        "keywords": ["hip hop", "rap", "beats"],
    },
    "rap": {"name": "Rap", "category": "Hip Hop", "keywords": ["rap", "rapper", "mc"]},
    "trap": {
        "name": "Trap",
        "category": "Hip Hop",
        "keywords": ["trap", "808", "southern rap"],
    },
    "drill": {
        "name": "Drill",
        "category": "Hip Hop",
        "keywords": ["drill", "uk drill", "chicago drill"],
    },
    "old_school": {
        "name": "Old School Hip Hop",
        "category": "Hip Hop",
        "keywords": ["old school", "90s rap", "boom bap"],
    },
    # R&B and Soul
    "rnb": {
        "name": "R&B",
        "category": "R&B/Soul",
        "keywords": ["r&b", "rnb", "rhythm and blues"],
    },
    "soul": {
        "name": "Soul",
        "category": "R&B/Soul",
        "keywords": ["soul", "motown", "neo soul"],
    },
    "funk": {
        "name": "Funk",
        "category": "R&B/Soul",
        "keywords": ["funk", "groove", "bass"],
    },
    "disco": {
        "name": "Disco",
        "category": "R&B/Soul",
        "keywords": ["disco", "70s", "dance floor"],
    },
    "gospel": {
        "name": "Gospel",
        "category": "R&B/Soul",
        "keywords": ["gospel", "spiritual", "church"],
    },
    # Traditional and Folk
    "jazz": {
        "name": "Jazz",
        "category": "Traditional",
        "keywords": ["jazz", "swing", "bebop"],
    },
    "blues": {
        "name": "Blues",
        "category": "Traditional",
        "keywords": ["blues", "12 bar", "delta"],
    },
    "classical": {
        "name": "Classical",
        "category": "Traditional",
        "keywords": ["classical", "orchestra", "symphony"],
    },
    "country": {
        "name": "Country",
        "category": "Traditional",
        "keywords": ["country", "nashville", "folk"],
    },
    "folk": {
        "name": "Folk",
        "category": "Traditional",
        "keywords": ["folk", "acoustic", "traditional"],
    },
    "bluegrass": {
        "name": "Bluegrass",
        "category": "Traditional",
        "keywords": ["bluegrass", "banjo", "appalachian"],
    },
    # Latin
    "latin": {
        "name": "Latin",
        "category": "Latin",
        "keywords": ["latin", "latino", "hispanic"],
    },
    "reggaeton": {
        "name": "Reggaeton",
        "category": "Latin",
        "keywords": ["reggaeton", "perreo", "dembow"],
    },
    "salsa": {
        "name": "Salsa",
        "category": "Latin",
        "keywords": ["salsa", "mambo", "cuban"],
    },
    "bachata": {
        "name": "Bachata",
        "category": "Latin",
        "keywords": ["bachata", "dominican", "guitar"],
    },
    "merengue": {
        "name": "Merengue",
        "category": "Latin",
        "keywords": ["merengue", "accordion", "fast"],
    },
    "cumbia": {
        "name": "Cumbia",
        "category": "Latin",
        "keywords": ["cumbia", "colombian", "accordion"],
    },
    "bossa_nova": {
        "name": "Bossa Nova",
        "category": "Latin",
        "keywords": ["bossa nova", "brazilian", "smooth"],
    },
    # Reggae and Caribbean
    "reggae": {
        "name": "Reggae",
        "category": "Reggae",
        "keywords": ["reggae", "jamaica", "rastafari"],
    },
    "dancehall": {
        "name": "Dancehall",
        "category": "Reggae",
        "keywords": ["dancehall", "jamaican", "ragga"],
    },
    "ska": {
        "name": "Ska",
        "category": "Reggae",
        "keywords": ["ska", "upstroke", "two tone"],
    },
    "dub": {"name": "Dub", "category": "Reggae", "keywords": ["dub", "echo", "reverb"]},
    # World Music
    "afrobeat": {
        "name": "Afrobeat",
        "category": "World",
        "keywords": ["afrobeat", "african", "fela"],
    },
    "flamenco": {
        "name": "Flamenco",
        "category": "World",
        "keywords": ["flamenco", "spanish", "guitar"],
    },
    "indian_classical": {
        "name": "Indian Classical",
        "category": "World",
        "keywords": ["raga", "sitar", "tabla"],
    },
    "celtic": {
        "name": "Celtic",
        "category": "World",
        "keywords": ["celtic", "irish", "fiddle"],
    },
    # Alternative and Indie
    "indie": {
        "name": "Indie",
        "category": "Alternative",
        "keywords": ["indie", "independent", "alternative"],
    },
    "shoegaze": {
        "name": "Shoegaze",
        "category": "Alternative",
        "keywords": ["shoegaze", "dreamy", "reverb"],
    },
    "post_rock": {
        "name": "Post Rock",
        "category": "Alternative",
        "keywords": ["post rock", "instrumental", "atmospheric"],
    },
    "emo": {
        "name": "Emo",
        "category": "Alternative",
        "keywords": ["emo", "emotional", "hardcore"],
    },
    # New Age and Chill
    "new_age": {
        "name": "New Age",
        "category": "Chill",
        "keywords": ["new age", "meditation", "spiritual"],
    },
    "lofi": {
        "name": "Lo-Fi",
        "category": "Chill",
        "keywords": ["lofi", "chill", "study beats"],
    },
    "chillout": {
        "name": "Chillout",
        "category": "Chill",
        "keywords": ["chillout", "relaxing", "downtempo"],
    },
}


# # yt-dlp configuration for audio extraction
# YT_DLP_AUDIO_OPTS = {
#     "format": "bestaudio/best",
#     "extractaudio": True,
#     "audioformat": "mp3",
#     "audioquality": "192",
#     "quiet": True,
#     "no_warnings": True,
#     "writesubtitles": False,
#     "writeautomaticsub": False,
#     "referer": "https://www.youtube.com/",
#     "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# }
