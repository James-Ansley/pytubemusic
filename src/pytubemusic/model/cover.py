from pathlib import Path
from urllib.parse import urlparse

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

    def as_uri(self) -> str:
        url = urlparse(self.href)
        if url.scheme == "":
            return urlparse("https://" + self.href).geturl()
        else:
            return url.geturl()


class File(Model):
    __match_args__ = ("path",)

    path: Path

    def as_uri(self) -> str:
        return self.path.resolve().as_uri()
