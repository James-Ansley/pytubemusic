import functools
import logging

logger = logging.getLogger("yourtubemusic")


def log_call(
        level=logging.INFO,
        on_enter: str = None,
        on_exit: str = None
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if on_enter is not None:
                logger.log(level, on_enter.format(*args, **kwargs))
            result = func(*args, **kwargs)
            if on_exit is not None:
                logger.log(level, on_exit.format(*args, **kwargs))
            return result

        return wrapper

    return decorator
