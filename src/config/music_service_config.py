"""
Configuraciones optimizadas para el servicio de música
"""

import os
from typing import Any, Dict

# Configuraciones para manejo de YouTube
YOUTUBE_SERVICE_CONFIG = {
    # Rate limiting más conservador
    "MIN_DELAY_BETWEEN_REQUESTS": 2.0,
    "MAX_CONCURRENT_DOWNLOADS": 2,
    "REQUEST_TIMEOUT": 45,
    # Configuración de reintentos
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 1.0,
    "EXPONENTIAL_BACKOFF": True,
    # Configuración de calidad de audio
    "PREFERRED_AUDIO_FORMAT": "bestaudio[ext=m4a]/bestaudio/best",
    "FALLBACK_AUDIO_FORMAT": "worstaudio/worst",
    "MAX_AUDIO_QUALITY": "320",  # kbps
    # Configuración anti-bot
    "USE_RANDOM_USER_AGENTS": True,
    "ROTATE_HEADERS": True,
    "USE_COOKIES": False,  # Cambiar a True si tienes cookies válidas
    # Timeouts y límites
    "SOCKET_TIMEOUT": 30,
    "READ_TIMEOUT": 60,
    "CONNECTION_POOL_SIZE": 5,
}

# Configuraciones para la base de datos de canciones
SONG_SERVICE_CONFIG = {
    # Límites de consulta
    "DEFAULT_SONGS_LIMIT": 50,
    "MAX_SONGS_LIMIT": 200,
    "RANDOM_SONGS_DEFAULT": 10,
    "RANDOM_SONGS_MAX": 20,
    # Cache configuración
    "ENABLE_SONG_CACHE": True,
    "SONG_CACHE_TTL": 3600,  # 1 hora
    "SEARCH_CACHE_TTL": 1800,  # 30 minutos
    # Configuración de procesamiento
    "BATCH_SIZE": 10,
    "MAX_PROCESSING_TIME": 300,  # 5 minutos
    # Configuración de limpieza automática
    "AUTO_CLEANUP_ENABLED": True,
    "CLEANUP_INACTIVE_DAYS": 30,
    "CLEANUP_BATCH_SIZE": 100,
}

# Configuraciones para logging optimizado
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} - {name} - {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/music_service.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/music_service_errors.log",
            "maxBytes": 5242880,  # 5MB
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "common.adapters.media": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.songs": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "common.utils.youtube_anti_bot": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "common.utils.youtube_error_handler": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# Configuraciones de Django optimizadas
DJANGO_OPTIMIZATIONS = {
    # Database optimizations
    "DATABASES": {
        "default": {
            "CONN_MAX_AGE": 600,  # 10 minutos
            "OPTIONS": {
                "MAX_CONNS": 20,
                "CHARSET": "utf8mb4",
                "use_unicode": True,
            },
        }
    },
    # Cache configuration
    "CACHES": {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 20,
                    "retry_on_timeout": True,
                },
            },
            "KEY_PREFIX": "streamflow_music",
            "TIMEOUT": 300,  # 5 minutos default
        }
    },
    # Session configuration
    "SESSION_ENGINE": "django.contrib.sessions.backends.cache",
    "SESSION_CACHE_ALIAS": "default",
    # Async configuration
    "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
    "USE_TZ": True,
    # Security optimizations
    "SECURE_BROWSER_XSS_FILTER": True,
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    "X_FRAME_OPTIONS": "DENY",
}


def get_music_service_settings() -> Dict[str, Any]:
    """Obtiene todas las configuraciones del servicio de música"""
    return {
        "youtube": YOUTUBE_SERVICE_CONFIG,
        "songs": SONG_SERVICE_CONFIG,
        "logging": LOGGING_CONFIG,
        "django": DJANGO_OPTIMIZATIONS,
    }


def apply_youtube_settings(base_config: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica configuraciones específicas de YouTube a una configuración base"""
    config = base_config.copy()

    # Aplicar configuraciones de YouTube
    youtube_config = YOUTUBE_SERVICE_CONFIG

    config.update(
        {
            "socket_timeout": youtube_config["SOCKET_TIMEOUT"],
            "retries": youtube_config["MAX_RETRIES"],
            "format": youtube_config["PREFERRED_AUDIO_FORMAT"],
            "geo_bypass": True,
            "no_check_certificate": False,
            "extract_flat": False,
            "quiet": True,
            "no_warnings": True,
        }
    )

    return config


def get_optimized_ydl_options() -> Dict[str, Any]:
    """Obtiene opciones optimizadas para yt-dlp basadas en pruebas exitosas"""

    return {
        # Formato de audio - funciona sin problemas
        "format": "bestaudio/best",
        "no_warnings": True,
        # Configuración de archivos
        # Configuración anti-detección que funciona
        "geo_bypass": True,
        # "outtmpl": file_path,
        "age_limit": 99,
        # "extractor_args": {
        #     "youtube": {"player_client": ["android", "web"], "skip": ["dash"]}
        # },
        "restrictfilenames": True,
        "windowsfilenames": True,
        "trim_filename": 100,
        # Sin FFmpeg para evitar problemas de conversión
        # Los archivos se descargan en formato nativo (webm/m4a)
        "extractaudio": False,  # No forzar extracción que requiere FFmpeg
        "quiet": True,
        # Configuración adicional para estabilidad
        "ignoreerrors": False,
        "logtostderr": False,
        "no_color": True,
    }
