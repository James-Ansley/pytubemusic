from datetime import timedelta
from pathlib import PurePath
from typing import IO

__all__ = (
    "MaybeInt",
    "MaybeFloat",
    "MaybeStr",
    "MaybePath",
    "MaybeTimedelta",
    "MaybeIO",
)


type MaybeInt = int | None
type MaybeFloat = float | None
type MaybeStr = str | None
type MaybePath = PurePath | None
type MaybeTimedelta = timedelta | None
type MaybeIO = IO | None
