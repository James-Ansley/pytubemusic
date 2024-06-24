from pathlib import Path

from .base import Model

__all__ = (
    "Cover",
    "MaybeCover",
    "Url",
    "File",
)

type Cover = File | Url
type MaybeCover = Cover | None


class Url(Model):
    __match_args__ = ("href",)

    href: str


class File(Model):
    __match_args__ = ("path",)

    path: Path
