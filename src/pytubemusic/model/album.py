from pydantic import Field

from .base import Model
from .cover import MaybeCover
from .tags import AlbumTags
from .track import *

__all__ = ("Album",)


class Album(Model):
    """A combination of individual tracks"""

    __match_args__ = ("metadata", "cover", "tracks")

    metadata: AlbumTags
    cover: MaybeCover = None
    tracks: tuple[Track, ...] = Field(min_items=1)