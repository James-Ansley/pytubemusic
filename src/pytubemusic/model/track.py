"""
Data types for collections of tracks
"""
from typing import Literal

from pydantic import Field

from .base import MaybeTimedelta, Model
from .cover import MaybeCover
from .tags import TrackTags

__all__ = (
    "Track",
    "Single",
    "Split",
    "Playlist",
    "MergePlaylist",
    "Merge",
    "TrackStub",
    "AudioStub",
    "TimeStub",
)

type Track = Single | Split | Playlist | MergePlaylist | Merge


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

    __match_args__ = ("metadata", "start", "end")

    metadata: TrackTags
    start: MaybeTimedelta = None
    end: MaybeTimedelta = None


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
    tracks: tuple[TrackStub | Literal["DROP"], ...] | None = None


class MergePlaylist(Model):
    """Playlist tracks combined into one"""

    __match_args__ = ("url", "metadata", "cover", "tracks")

    url: str = Field(pattern=r"/playlist\?list=")
    metadata: TrackTags
    cover: MaybeCover = None
    tracks: tuple[TimeStub | Literal["DROP"], ...] | None = None


class Merge(Model):
    """Multiple tacks combined into one"""

    __match_args__ = ("metadata", "cover", "tracks")

    metadata: TrackTags
    cover: MaybeCover = None
    tracks: tuple[AudioStub, ...] = Field(min_length=1)
