import functools
import sys
from collections.abc import Callable
from typing import Never, NoReturn

from cowsay import cowsay, get_random_cow

__all__ = ("panic", "panic_on_error", "never")


def panic(msg: str, wrap: bool = True) -> NoReturn:
    """
    Prints the given message to stderr and exists with a status code of 1.
    The message is formatted in a humorous cow.

    :param msg: The message to print
    :param wrap: Whether output in the cowsay text should be wrapped
    """
    print(
        cowsay(msg, cow=get_random_cow(), wrap_text=wrap),
        file=sys.stderr,
    )
    sys.exit(1)


def panic_on_error[** P, R, E: type[Exception]](
      msg: str | Callable[[E, P], str],
      catch: E | tuple[E, ...] = Exception,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Returns a decorator that panics if the wrapped function raises an error
    covered by ``catch``.

    :param msg: A string or a lambda that takes the decorated function's
        error value and parameters and returns a string.
    :param catch: The exceptions that will be caught by this logger.
    :return: A decorator
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except catch as e:
                if isinstance(msg, Callable):
                    message = msg(e, *args, **kwargs)
                else:
                    message = msg
                panic(message, wrap=False)

        return wrapper

    return decorator


def never(arg: Never) -> NoReturn:
    raise panic(
        "This function shouldn't be called. "
        "It was given a value that should have been type Never:\n"
        f"{arg}"
    )
