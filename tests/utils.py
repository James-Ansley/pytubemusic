from types import FunctionType


def test[T: FunctionType](f: T) -> T:
    setattr(f, "__test__", True)
    return f
