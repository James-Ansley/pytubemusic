import functools
import inspect
import logging
from textwrap import indent

logger = logging.getLogger("pytubemusic")

INDENT_WIDTH = 2
_INDENT = 0


def log_call(
        level=logging.INFO,
        on_enter: str = None,
        on_exit: str = None,
        on_error: str = None,
):

    def decorator(func):
        arg_spec = inspect.getfullargspec(func)
        params = arg_spec.args

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global _INDENT
            fmt_kwargs = dict(zip(params, args)) | kwargs
            fmt_args = [fmt_kwargs.get(n, "") for n in params]

            log_message(on_enter, fmt_args, fmt_kwargs, level)

            _INDENT += INDENT_WIDTH
            try:
                result = func(*args, **kwargs)
                _INDENT -= INDENT_WIDTH
            except Exception as e:
                _INDENT -= INDENT_WIDTH
                log_message(on_error, fmt_args, fmt_kwargs, level)
                raise e
            else:
                log_message(on_exit, fmt_args, fmt_kwargs, level)

            return result

        return wrapper

    return decorator


def log_message(msg, fmt_args, fmt_kwargs, level):
    if msg is not None:
        msg = indent(msg, " " * _INDENT).format(*fmt_args, **fmt_kwargs)
        logger.log(level, msg)
