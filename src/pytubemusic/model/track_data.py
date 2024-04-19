from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Self

from .album import Album
from .base import MaybeStr, MaybeTimedelta
from .cover import MaybeCover
from .tags import Tags
from .track import *

__all__ = ("TrackData", "AudioData", "PlaylistAudioData")

from ..utils import never


@dataclass(frozen=True)
class AudioData:
    url: str
    start: MaybeTimedelta = None
    end: MaybeTimedelta = None


@dataclass(frozen=True)
class PlaylistAudioData:
    url: str
    index: int
    start: MaybeTimedelta = None
    end: MaybeTimedelta = None


@dataclass(frozen=True)
class TrackData:
    metadata: Tags
    cover: MaybeStr
    track_parts: Sequence[AudioData | PlaylistAudioData]

    @classmethod
    def from_album(cls, album: Album) -> Iterator[Self]:
        tracks = [
            track_data
            for track in album.tracks
            for track_data in cls.from_track(track, album.metadata, album.cover)
        ]
        for i, track in enumerate(tracks, start=1):
            yield TrackData(
                metadata=track.metadata + Tags(track=i),
                cover=track.cover,
                track_parts=track.track_parts,
            )

    @classmethod
    def from_track(
          cls,
          track: Track,
          tags: Tags = Tags(),
          cover: MaybeCover = None,
    ) -> Iterator[Self]:
        match track:
            case Single():
                yield from cls.from_single(tags, cover, track)
            case Split():
                yield from cls.from_split(tags, cover, track)
            case Playlist():
                yield from cls.from_playlist(tags, cover, track)
            case MergePlaylist():
                yield from cls.from_merge_playlist(tags, cover, track)
            case Merge():
                yield from cls.from_merge(tags, cover, track)
            case _:
                never(track)

    @classmethod
    def from_playlist(
          cls,
          tags: Tags,
          cover: MaybeCover,
          track: Playlist,
    ) -> Iterator[Self]:
        cover = track.cover or cover
        for i, stub in enumerate(track.tracks):
            if stub == "DROP":
                continue
            yield cls(
                metadata=stub.metadata + tags,
                cover=cover.as_uri() if cover is not None else None,
                track_parts=(
                    PlaylistAudioData(track.url, i, stub.start, stub.end),
                )
            )

    @classmethod
    def from_split(
          cls,
          tags: Tags,
          cover: MaybeCover,
          track: Split,
    ) -> Iterator[Self]:
        cover = track.cover or cover
        for i in range(len(track.tracks) - 1):
            yield cls(
                metadata=track.tracks[i].metadata + tags,
                cover=cover.as_uri() if cover is not None else None,
                track_parts=(
                    AudioData(
                        url=track.url,
                        start=track.tracks[i].start,
                        end=track.tracks[i].end or track.tracks[i + 1].start
                    ),
                ),
            )
        last = track.tracks[-1]
        yield cls(
            metadata=last.metadata + tags,
            cover=cover.as_uri() if cover is not None else None,
            track_parts=(
                AudioData(url=track.url, start=last.start, end=last.end),
            )
        )

    @classmethod
    def from_single(
          cls,
          tags: Tags,
          cover: MaybeCover,
          track: Single,
    ) -> Iterator[Self]:
        cover = track.cover or cover
        yield cls(
            metadata=track.metadata + tags,
            cover=cover.as_uri() if cover is not None else None,
            track_parts=(
                AudioData(url=track.url, start=track.start, end=track.end),
            ),
        )

    @classmethod
    def from_merge_playlist(
          cls,
          tags: Tags,
          cover: MaybeCover,
          track: MergePlaylist
    ) -> Iterator[Self]:
        cover = track.cover or cover
        yield cls(
            metadata=track.metadata + tags,
            cover=cover.as_uri() if cover is not None else None,
            track_parts=tuple(
                PlaylistAudioData(track.url, i, stub.start, stub.end)
                for i, stub in enumerate(track.tracks)
                if stub != "DROP"
            ),
        )

    @classmethod
    def from_merge(
          cls,
          tags: Tags,
          cover: MaybeCover,
          track: Merge
    ) -> Iterator[Self]:
        cover = track.cover or cover
        yield TrackData(
            metadata=track.metadata + tags,
            cover=cover.as_uri() if cover is not None else None,
            track_parts=tuple(
                AudioData(stub.url, stub.start, stub.end)
                for stub in track.tracks
            )
        )
