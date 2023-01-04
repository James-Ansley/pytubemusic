import functools
import logging
from textwrap import indent

logger = logging.getLogger("pytubemusic")

indent_width = 2

stack_depth = 0


def log_call(
        level=logging.INFO,
        on_enter: str = None,
        on_exit: str = None
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global stack_depth
            space = " " * indent_width * stack_depth
            if on_enter is not None:
                logger.log(
                    level,
                    indent(on_enter, space).format(*args, **kwargs)
                )
            stack_depth += 1
            result = func(*args, **kwargs)
            stack_depth -= 1
            if on_exit is not None:
                logger.log(
                    level,
                    indent(on_exit, space).format(*args, **kwargs)
                )
            return result

        return wrapper

    return decorator
