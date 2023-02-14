import contextlib
import functools
import inspect
import logging
from textwrap import indent

logger = logging.getLogger("pytubemusic")

INDENT_WIDTH = 2
_INDENT = 0


@contextlib.contextmanager
def log_block(
        level=logging.INFO,
        on_enter: str = None,
        on_exit: str = None,
        on_error: str = None):
    """
    Logs entering, exiting, and errors in a block of code.
    Calls to log_block are on a "global stack" where each nested call is
    indented by a global INDENT_WIDTH.
    """
    global _INDENT, INDENT_WIDTH
    try:
        log_message(on_enter, [], {}, level)
        _INDENT += INDENT_WIDTH
        yield
        _INDENT -= INDENT_WIDTH
    except Exception as e:
        _INDENT -= INDENT_WIDTH
        log_message(on_error, [], {}, level)
        raise e
    else:
        log_message(on_exit, [], {}, level)


def log_call(
        level=logging.INFO,
        on_enter: str = None,
        on_exit: str = None,
        on_error: str = None,
):
    """
    Logs calls – on a "global stack" where each nested call is indented
    by a global INDENT_WIDTH.
    """
    def decorator(func):
        arg_spec = inspect.getfullargspec(func)
        params = arg_spec.args

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global _INDENT, INDENT_WIDTH
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
