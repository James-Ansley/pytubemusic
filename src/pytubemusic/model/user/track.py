"""
Data types for collections of tracks
"""
from typing import Literal

from pydantic import Field, RootModel

from pytubemusic.model.types import MaybeTimedelta
from .base import Model
from .cover import MaybeCover
from .tags import TrackTags

__all__ = (
    "Track",
    "TrackType",
    "Single",
    "Split",
    "Playlist",
    "Merge",
    "TrackStub",
    "AudioStub",
    "TimeStub",
    "MergeStub",
    "Drop",
)

type TrackType = Single | Split | Playlist | Merge


class Track:
    def __new__(cls, **kwargs) -> TrackType:
        # noinspection PyTypeChecker
        return RootModel[TrackType](**kwargs).root


class Single(Model):
    """A single track"""

    __match_args__ = ("url", "metadata", "cover", "start", "end")

    url: str = Field(pattern=r"/watch\?v=")
    metadata: TrackTags
    cover: MaybeCover = None
    start: MaybeTimedelta = None
    end: MaybeTimedelta = None


class TrackStub(Model):
    """A track that exists as a segment of a larger track"""

    __match_args__ = ("metadata", "cover", "start", "end")

    metadata: TrackTags
    cover: MaybeCover = None
    start: MaybeTimedelta = None
    end: MaybeTimedelta = None


class Drop(Model):
    __match_args__ = ("drop",)

    drop: Literal[True] = True


class AudioStub(Model):
    """A track used only for audio with no associated metadata"""

    __match_args__ = ("url", "start", "end")

    url: str = Field(pattern=r"/watch\?v=")
    start: MaybeTimedelta = None
    end: MaybeTimedelta = None


class TimeStub(Model):
    """Timestamp information"""

    __match_args__ = ("url", "start", "end")

    start: MaybeTimedelta = None
    end: MaybeTimedelta = None


class MergeStub(Model):
    """Multiple time stamps clamped into one"""

    __match_args__ = ("metadata", "cover", "parts")

    metadata: TrackTags
    cover: MaybeCover = None
    parts: tuple[TimeStub | Drop, ...]


class Split(Model):
    """A single track that is split into smaller individual tracks"""

    __match_args__ = ("url", "cover", "tracks")

    url: str = Field(pattern=r"/watch\?v=")
    cover: MaybeCover = None
    tracks: tuple[TrackStub, ...] = Field(min_length=1)


class Playlist(Model):
    """A playlist"""

    __match_args__ = ("url", "cover", "tracks")

    url: str = Field(pattern=r"/playlist\?list=")
    cover: MaybeCover = None
    tracks: tuple[TrackStub | MergeStub | Drop, ...] = ()


class Merge(Model):
    """Multiple tacks combined into one"""

    __match_args__ = ("metadata", "cover", "tracks")

    metadata: TrackTags
    cover: MaybeCover = None
    parts: tuple[AudioStub, ...] = Field(min_length=1)
