<<<<<<< HEAD
"""
Utilidad para manejo de reintentos con backoff exponencial
"""

import asyncio
import random
=======
import secrets
import time
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
from typing import Any, Callable, Type

from ..mixins.logging_mixin import LoggingMixin


class RetryManager(LoggingMixin):
<<<<<<< HEAD
    """Gestiona reintentos con backoff exponencial y jitter"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
=======
    def __init__(
        self,
        max_retries=3,
        base_delay=1.0,
        max_delay=60.0,
        backoff_factor=2.0,
        jitter=True,
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
    ):
        super().__init__()
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

<<<<<<< HEAD
    async def execute_with_retry(
        self, func: Callable[..., Any], *args, **kwargs
    ) -> Any:
        """Ejecuta una función con reintentos automáticos"""
        last_exception = None  # noqa

        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except Exception as e:
                last_exception = e  # noqa

                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(
                        f"All {self.max_retries + 1} attempts failed. "
                        f"Last error: {str(e)}"
=======
    def execute_with_retry(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        _ = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                _ = e
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"All {self.max_retries + 1} attempts failed. Last error: {str(e)}"
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
                    )

        return None

    def _calculate_delay(self, attempt: int) -> float:
<<<<<<< HEAD
        """Calcula el delay para el siguiente intento"""
        delay = min(self.base_delay * (self.backoff_factor**attempt), self.max_delay)

        if self.jitter:
            # Añadir jitter para evitar thundering herd
            delay *= 0.5 + random.random() * 0.5  # nosec B311

=======
        delay = min(self.base_delay * (self.backoff_factor**attempt), self.max_delay)
        if self.jitter:
            delay *= 0.5 + secrets.SystemRandom().random() * 0.5
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
        return delay


class CircuitBreaker(LoggingMixin):
<<<<<<< HEAD
    """Implementa el patrón Circuit Breaker"""

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
    ):
        super().__init__()
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

<<<<<<< HEAD
    async def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Ejecuta una función a través del circuit breaker"""
=======
    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")  # noqa

        try:
<<<<<<< HEAD
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            self._on_success()
            return result

=======
            result = func(*args, **kwargs)
            self._on_success()
            return result
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
<<<<<<< HEAD
        """Determina si se debe intentar resetear el circuit breaker"""
        return (
            self.last_failure_time is not None
            and asyncio.get_event_loop().time() - self.last_failure_time
            >= self.recovery_timeout
        )

    def _on_success(self):
        """Maneja el éxito de una operación"""
=======
        if self.last_failure_time is None:
            return False
        return time.monotonic() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.logger.info("Circuit breaker reset to CLOSED")

    def _on_failure(self):
<<<<<<< HEAD
        """Maneja el fallo de una operación"""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
=======
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )
