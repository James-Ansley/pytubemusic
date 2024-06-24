import functools
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
from urllib.request import urlopen

from pytubemusic.logging import log
from pytubemusic.model import MaybeIO, MaybePath, MaybeStr
from pytubemusic.model.user import File, MaybeCover, Url


@functools.lru_cache(maxsize=1)
def fetch_cover_data(cover: MaybeCover, context: MaybePath = None) -> MaybeIO:
    uri = as_uri(cover, context)
    log(f"Fetching cover: {uri}")
    if uri is None:
        return None
    else:
        data = fetch_uri(uri)
        return as_named_temp_file(data, ".jpg")


def as_named_temp_file(data: bytes, ext: MaybeStr = None) -> NamedTemporaryFile:
    f = NamedTemporaryFile("wb", suffix=ext)
    f.write(data)
    return f


def fetch_uri(uri: str) -> bytes:
    with urlopen(uri) as f:
        return f.read()


def as_uri(cover: MaybeCover, context: MaybePath = None) -> MaybeStr:
    match cover:
        case None:
            return None
        case File(path):
            context = Path.cwd() if context is None else context
            if os.path.isabs(path):
                return path.resolve().as_uri()
            else:
                return context.joinpath(path).resolve().as_uri()
        case Url(href):
            url = urlparse(href)
            if url.scheme == "":
                return urlparse("https://" + href).geturl()
            else:
                return url.geturl()
