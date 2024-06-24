from contextlib import AbstractContextManager, contextmanager
from typing import IO


@contextmanager
def stream[T: IO](buff: T) -> AbstractContextManager[T]:
    try:
        yield buff
    finally:
        buff.seek(0)
