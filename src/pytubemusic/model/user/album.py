from pydantic import Field

from .base import Model
from .cover import MaybeCover
from .tags import AlbumTags
from .track import TrackType

__all__ = ("Album",)


class Album(Model):
    """A combination of individual tracks"""

    __match_args__ = ("metadata", "cover", "tracks")

    metadata: AlbumTags
    cover: MaybeCover = None
    tracks: tuple[TrackType, ...] = Field(min_length=1)
