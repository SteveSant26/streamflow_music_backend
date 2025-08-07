"""
Timeout decorator for performance critical operations (Windows compatible)
"""

import functools
import threading
from typing import Any, Callable


class TimeoutError(Exception):
    """Raised when operation exceeds timeout"""


def timeout_after(seconds: int):
    """
    Decorator that adds timeout to function execution using threading

    Args:
        seconds: Timeout in seconds
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result: list = [None]
            exception: list = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)

            if thread.is_alive():
                # Thread is still running, operation timed out
                raise TimeoutError(
                    f"Function {func.__name__} timed out after {seconds} seconds"
                )

            if exception[0]:
                raise exception[0]

            return result[0]

        return wrapper

    return decorator
