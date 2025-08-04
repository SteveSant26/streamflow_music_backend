import logging
import logging.config
import sys
from pathlib import Path


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, "pathname"):
            project_root = Path(__file__).resolve().parents[2]
            try:
                record.filename = str(
                    Path(record.pathname).relative_to(project_root)
                ).replace("\\", "/")
            except ValueError:
                record.filename = Path(record.pathname).name
        return super().format(record)


class LoggingConfig:
    @staticmethod
    def get_logging_config(debug: bool = False, env: str = "dev") -> dict:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        formatter_style = {
            "detailed": {
                "()": CustomFormatter,
                "format": "[{asctime}] {levelname} - {filename}:{lineno} in {funcName}() - {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "console": {
                "()": CustomFormatter,
                "format": (
                    "{levelname} - {filename}:{lineno} - {message}"
                    if debug
                    else "[{asctime}] {levelname} - {message}"
                ),
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        }

        handlers = {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG" if debug else "INFO",
                "formatter": "console",
                "stream": sys.stdout,
            },
            "file_info": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": f"logs/{env}.log",
                "maxBytes": 10_485_760,
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "file_error": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": f"logs/{env}_errors.log",
                "maxBytes": 10_485_760,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        }

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatter_style,
            "handlers": handlers,
            "loggers": {
                "app": {
                    "level": "DEBUG" if debug else "INFO",
                    "handlers": ["console", "file_info", "file_error"],
                    "propagate": False,
                },
                # Logger específico para detectar problemas de middleware async
                "django.request": {
                    "level": "DEBUG",
                    "handlers": ["console", "file_info"],
                    "propagate": False,
                },
                # Puedes agregar loggers para librerías específicas si quieres
            },
            "root": {
                "level": "DEBUG" if debug else "INFO",
                "handlers": ["console", "file_info", "file_error"],
            },
        }

    @staticmethod
    def setup_logging(debug: bool = False, env: str = "dev") -> logging.Logger:
        config = LoggingConfig.get_logging_config(debug, env)
        logging.config.dictConfig(config)
        logger = logging.getLogger("app")
        logger.info("Logging configured successfully")
        return logger


def get_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(name)
