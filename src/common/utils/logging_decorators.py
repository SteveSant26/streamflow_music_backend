import asyncio
import functools
import time
from typing import Any, Callable, Tuple

from .logging_config import get_logger

logger = get_logger("decorators")


def _get_class_name(args: tuple) -> str:
    """Extract class name from function arguments."""
    if not args or not hasattr(args[0], "__class__"):
        return ""
    return f"{args[0].__class__.__name__}."


def _should_include_args(include_args: bool, args: tuple, kwargs: dict) -> bool:
    """Check if arguments should be included in logging."""
    return include_args and (bool(args) or bool(kwargs))


def _format_arguments(args: tuple, kwargs: dict, has_class: bool) -> str:
    """Format function arguments for logging."""
    if not args and not kwargs:
        return ""

    display_args = args[1:] if has_class else args
    args_str = ", ".join([repr(arg) for arg in display_args])
    kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in kwargs.items()])
    all_args = ", ".join(filter(None, [args_str, kwargs_str]))
    return f"({all_args})" if all_args else "()"


def _should_include_result(include_result: bool, result: Any) -> bool:
    """Check if result should be included in logging."""
    return include_result and result is not None


def _format_result(result: Any, include_result: bool) -> str:
    """Format function result for logging."""
    if not _should_include_result(include_result, result):
        return ""
    return f" -> {type(result).__name__}"


def _log_message(logger_instance, level: str, message: str) -> None:
    """Log message with specified level."""
    getattr(logger_instance, level.lower())(message)


def _get_execution_context(
    func: Callable, args: tuple, include_args: bool
) -> tuple[str, str, str]:
    """Extract execution context information."""
    func_name = func.__name__
    class_name = _get_class_name(args)
    args_info = ""

    if _should_include_args(include_args, args, {}):
        args_info = _format_arguments(args, {}, bool(class_name))

    return func_name, class_name, args_info


def _log_execution_start(
    func_name: str, class_name: str, args_info: str, log_level: str
) -> None:
    """Log the start of function execution."""
    _log_message(logger, log_level, f"→ {class_name}{func_name}{args_info}")


def _log_execution_success(
    func_name: str,
    class_name: str,
    result: Any,
    duration: float,
    include_result: bool,
    log_level: str,
) -> None:
    """Log successful function execution."""
    result_info = _format_result(result, include_result)
    _log_message(
        logger, log_level, f"← {class_name}{func_name}{result_info} ({duration:.3f}s)"
    )


def _log_execution_error(
    func_name: str, class_name: str, error: Exception, duration: float
) -> None:
    """Log failed function execution."""
    logger.error(f"✗ {class_name}{func_name} failed: {str(error)} ({duration:.3f}s)")


def _execute_with_logging(
    func: Callable,
    args: tuple,
    kwargs: dict,
    func_name: str,
    class_name: str,
    include_args: bool,
    include_result: bool,
    log_level: str,
) -> Tuple[Any, float]:
    """Execute function with logging and return result and duration."""
    args_info = ""
    if _should_include_args(include_args, args, kwargs):
        args_info = _format_arguments(args, kwargs, bool(class_name))

    _log_execution_start(func_name, class_name, args_info, log_level)

    start_time = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        _log_execution_success(
            func_name, class_name, result, duration, include_result, log_level
        )
        return result, duration
    except Exception as e:
        duration = time.perf_counter() - start_time
        _log_execution_error(func_name, class_name, e, duration)
        raise


async def _async_execute_with_logging(
    func: Callable,
    args: tuple,
    kwargs: dict,
    func_name: str,
    class_name: str,
    include_args: bool,
    include_result: bool,
    log_level: str,
) -> Tuple[Any, float]:
    """Execute async function with logging and return result and duration."""
    args_info = ""
    if _should_include_args(include_args, args, kwargs):
        args_info = _format_arguments(args, kwargs, bool(class_name))

    _log_execution_start(func_name, class_name, args_info, log_level)

    start_time = time.perf_counter()
    try:
        result = await func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        _log_execution_success(
            func_name, class_name, result, duration, include_result, log_level
        )
        return result, duration
    except Exception as e:
        duration = time.perf_counter() - start_time
        _log_execution_error(func_name, class_name, e, duration)
        raise


def log_execution(
    include_args: bool = False, include_result: bool = False, log_level: str = "DEBUG"
):
    """
    Decorador que registra la ejecución de métodos/funciones, soporta async y sync.

    Args:
        include_args: Si incluir los argumentos en el log
        include_result: Si incluir el resultado en el log
        log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR)
    """

    def decorator(func: Callable) -> Callable:
        is_coroutine = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            func_name = func.__name__
            class_name = _get_class_name(args)

            result, _ = await _async_execute_with_logging(
                func,
                args,
                kwargs,
                func_name,
                class_name,
                include_args,
                include_result,
                log_level,
            )
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            func_name = func.__name__
            class_name = _get_class_name(args)

            result, _ = _execute_with_logging(
                func,
                args,
                kwargs,
                func_name,
                class_name,
                include_args,
                include_result,
                log_level,
            )
            return result

        return async_wrapper if is_coroutine else sync_wrapper

    return decorator


def _log_slow_execution(
    func_name: str, class_name: str, duration: float, threshold: float
) -> None:
    """Log slow execution warning."""
    logger.warning(
        f"⚠️  SLOW EXECUTION: {class_name}{func_name} took {duration:.3f}s "
        f"(threshold: {threshold}s)"
    )


def _is_slow_execution(duration: float, threshold: float) -> bool:
    """Check if execution time exceeds threshold."""
    return duration > threshold


def _check_and_log_performance(
    func: Callable, args: tuple, duration: float, threshold: float
) -> None:
    """Check performance and log if threshold exceeded."""
    if not _is_slow_execution(duration, threshold):
        return

    class_name = _get_class_name(args)
    _log_slow_execution(func.__name__, class_name, duration, threshold)


def log_performance(threshold_seconds: float = 1.0):
    """
    Decorador que registra métodos que tardan más de un umbral específico.
    Soporta funciones async y sync.
    """

    def decorator(func: Callable) -> Callable:
        is_coroutine = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start

            _check_and_log_performance(func, args, duration, threshold_seconds)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start

            _check_and_log_performance(func, args, duration, threshold_seconds)
            return result

        return async_wrapper if is_coroutine else sync_wrapper

    return decorator
