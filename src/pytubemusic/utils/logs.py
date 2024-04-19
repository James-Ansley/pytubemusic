import functools
import logging
from collections.abc import Callable

from enum import Enum

__all__ = (
    "LOGGER",
    "on_enter",
    "on_exit",
    "on_error",
    "LogLevel",
    "setup_handler",
)

LOGGER = logging.getLogger("pytubemusic")


class LogLevel(Enum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


def setup_handler(
        handler: logging.Handler,
        level: int | LogLevel = logging.INFO,
        logger: logging.Logger = LOGGER,
) -> None:
    if isinstance(level, LogLevel):
        level = level.value
    logger.setLevel(level)
    logger.addHandler(handler)


def on_enter[**P, R](
        msg: str | Callable[P, str],
        level: int = logging.INFO,
        logger: logging.Logger = LOGGER,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Returns a decorator that logs function calls. Logs are emitted before
    calling the function.

    :param msg: A log string or a lambda that takes the decorated function's
        parameters and returns a string.
    :param level: The log level.
    :param logger: The logging channel
    :return: A decorator
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            message = msg(*args, **kwargs) if isinstance(msg, Callable) else msg
            logger.log(level, message)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def on_exit[**P, R](
        msg: str | Callable[[R, P], str],
        level: int = logging.INFO,
        logger: logging.Logger = LOGGER,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Returns a decorator that logs function calls. Logs are emitted as
    the function returns.

    :param msg: A log string or a lambda that takes the decorated function's
        return value as a parameter and returns a string.
    :param level: The log level.
    :param logger: The logging channel
    :return: A decorator
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            message = msg(result, *args, **kwargs) if isinstance(msg, Callable) else msg
            logger.log(level, message)
            return result

        return wrapper

    return decorator


def on_error[**P, R, E: type[Exception]](
        msg: str | Callable[[E, P], str],
        level: int = logging.ERROR,
        catch: E | tuple[E, ...] = Exception,
        logger: logging.Logger = LOGGER,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Returns a decorator that logs function calls. Logs are emitted as
    the function returns.

    :param msg: A log string or a lambda that takes the decorated function's
        return value as a parameter and returns a string.
    :param level: The log level.
    :param catch: The exceptions that will be caught by this logger.
    :param logger: The logging channel
    :return: A decorator
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except catch as e:
                message = msg(e, *args, **kwargs) if isinstance(msg, Callable) else msg
                logger.log(level, message)
                raise e

        return wrapper

    return decorator
