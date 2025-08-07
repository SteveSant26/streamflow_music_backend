import logging
import re
import secrets
from enum import Enum
from typing import Dict, List, Tuple


class YouTubeErrorType(Enum):
    """Tipos de errores de YouTube"""

    RATE_LIMIT = "rate_limit"
    FORBIDDEN = "forbidden"
    UNAVAILABLE = "unavailable"
    NETWORK = "network"
    FORMAT_NOT_AVAILABLE = "format_not_available"
    REGION_BLOCKED = "region_blocked"
    UNKNOWN = "unknown"


class YouTubeErrorHandler:
    """Maneja errores específicos de YouTube y sugiere estrategias de recuperación"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_patterns = self._build_error_patterns()
        self.recovery_strategies = self._build_recovery_strategies()

    def _build_error_patterns(self) -> Dict[YouTubeErrorType, List[str]]:
        """Construye patrones de errores conocidos"""
        return {
            YouTubeErrorType.RATE_LIMIT: [
                r"too many requests",
                r"rate limit",
                r"quota exceeded",
                r"429",
                r"slow down",
            ],
            YouTubeErrorType.FORBIDDEN: [
                r"http error 403",
                r"forbidden",
                r"access denied",
                r"not authorized",
            ],
            YouTubeErrorType.UNAVAILABLE: [
                r"video.{0,20}unavailable",
                r"this video is not available",
                r"video has been removed",
                r"private video",
                r"members-only",
            ],
            YouTubeErrorType.FORMAT_NOT_AVAILABLE: [
                r"requested format.{0,20}not available",
                r"no video formats found",
                r"format selection failed",
            ],
            YouTubeErrorType.REGION_BLOCKED: [
                r"blocked in your country",
                r"not available in your country",
                r"geo.{0,20}block",
                r"region.{0,20}restrict",
            ],
            YouTubeErrorType.NETWORK: [
                r"connection.{0,20}timeout",
                r"network error",
                r"dns.{0,20}resolution.{0,20}failed",
                r"connection refused",
            ],
        }

    def _build_recovery_strategies(self) -> Dict[YouTubeErrorType, Dict]:
        """Construye estrategias de recuperación para cada tipo de error"""
        return {
            YouTubeErrorType.RATE_LIMIT: {
                "delay_range": (15.0, 60.0),
                "exponential_backoff": True,
                "max_retries": 3,
                "suggested_config_changes": [
                    "reduce_concurrent_requests",
                    "increase_delays",
                ],
            },
            YouTubeErrorType.FORBIDDEN: {
                "delay_range": (5.0, 15.0),
                "exponential_backoff": False,
                "max_retries": 2,
                "suggested_config_changes": ["use_different_client", "bypass_age_gate"],
            },
            YouTubeErrorType.UNAVAILABLE: {
                "delay_range": (0.0, 0.0),
                "exponential_backoff": False,
                "max_retries": 0,
                "suggested_config_changes": [],
            },
            YouTubeErrorType.FORMAT_NOT_AVAILABLE: {
                "delay_range": (1.0, 3.0),
                "exponential_backoff": False,
                "max_retries": 3,
                "suggested_config_changes": [
                    "use_worst_quality",
                    "try_different_formats",
                ],
            },
            YouTubeErrorType.REGION_BLOCKED: {
                "delay_range": (0.0, 0.0),
                "exponential_backoff": False,
                "max_retries": 1,
                "suggested_config_changes": ["use_proxy", "geo_bypass"],
            },
            YouTubeErrorType.NETWORK: {
                "delay_range": (3.0, 10.0),
                "exponential_backoff": True,
                "max_retries": 3,
                "suggested_config_changes": [
                    "increase_timeout",
                    "retry_with_different_resolver",
                ],
            },
        }

    def classify_error(self, error_message: str) -> YouTubeErrorType:
        """Clasifica un error basado en el mensaje"""
        error_text = error_message.lower()

        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_text, re.IGNORECASE):
                    return error_type

        return YouTubeErrorType.UNKNOWN

    def get_recovery_strategy(
        self, error_type: YouTubeErrorType, attempt_number: int = 1
    ) -> Dict:
        """Obtiene la estrategia de recuperación para un tipo de error"""
        strategy = self.recovery_strategies.get(error_type, {})

        if not strategy:
            return {"should_retry": False, "delay": 0.0, "config_changes": []}

        max_retries = strategy.get("max_retries", 0)
        should_retry = attempt_number <= max_retries

        if not should_retry:
            return {"should_retry": False, "delay": 0.0, "config_changes": []}

        # Calcular delay
        delay_range = strategy.get("delay_range", (1.0, 3.0))
        base_delay = secrets.SystemRandom().uniform(delay_range[0], delay_range[1])

        if strategy.get("exponential_backoff", False):
            base_delay *= 2 ** (attempt_number - 1)

        return {
            "should_retry": True,
            "delay": base_delay,
            "config_changes": strategy.get("suggested_config_changes", []),
            "error_type": error_type.value,
        }

    def handle_error(
        self, error_message: str, attempt_number: int = 1
    ) -> Tuple[bool, float, List[str]]:
        """
        Maneja un error y retorna estrategia de recuperación

        Returns:
            Tuple de (should_retry, delay_seconds, config_suggestions)
        """
        error_type = self.classify_error(error_message)
        strategy = self.get_recovery_strategy(error_type, attempt_number)

        self.logger.warning(
            f"YouTube error classified as {error_type.value}, "
            f"attempt {attempt_number}, strategy: {strategy}"
        )

        return (
            strategy["should_retry"],
            strategy["delay"],
            strategy.get("config_changes", []),
        )

    def log_error_stats(self, error_counts: Dict[YouTubeErrorType, int]):
        """Registra estadísticas de errores para análisis"""
        if not error_counts:
            return

        self.logger.info("YouTube Error Statistics:")
        for error_type, count in error_counts.items():
            self.logger.info(f"  {error_type.value}: {count}")
