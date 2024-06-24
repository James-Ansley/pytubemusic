"""
Normalized track data
"""
import itertools
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Self

from pytubemusic.model.types import MaybeFloat, MaybeTimedelta
from pytubemusic.model.user import (Album, Drop, MaybeCover, MediaType, Merge,
                                    MergeStub, Playlist, Single, Split, Tags,
                                    TrackStub, TrackTags, TrackType)

__all__ = ("AudioData", "PlaylistAudioData", "TrackData")


@dataclass(frozen=True)
class AudioData:
    url: str
    start: MaybeTimedelta = None
    end: MaybeTimedelta = None

    def start_second(self) -> MaybeFloat:
        return self.start.total_seconds() if self.start is not None else None

    def duration_seconds(self) -> MaybeFloat:
        if self.start is None and self.end is not None:
            return self.end.total_seconds()
        elif self.start is not None and self.end is not None:
            return (self.end - self.start).total_seconds()
        else:
            return None


@dataclass(frozen=True)
class PlaylistAudioData:
    url: str
    index: int
    start: MaybeTimedelta = None
    end: MaybeTimedelta = None

    def start_second(self) -> MaybeFloat:
        return self.start.total_seconds() if self.start is not None else None

    def duration_seconds(self) -> MaybeFloat:
        if self.start is None and self.end is not None:
            return self.end.total_seconds()
        elif self.start is not None and self.end is not None:
            return (self.end - self.start).total_seconds()
        else:
            return None


@dataclass(frozen=True)
class TrackData:
    metadata: Tags
    cover: MaybeCover
    parts: Sequence[AudioData | PlaylistAudioData]

    @classmethod
    def from_media(cls, media: MediaType) -> Iterator[Self]:
        match media:
            case Album():
                yield from cls.from_album(media)
            case Single() | Split() | Playlist() | Merge():
                yield from cls.from_track(media)

    @classmethod
    def from_album(cls, album: Album) -> Iterator[Self]:
        tracks = (
            track
            for album_tracks in album.tracks
            for track in cls.from_track(album_tracks)
        )
        for i, track in enumerate(tracks, start=1):
            yield TrackData(
                metadata=track.metadata + album.metadata + Tags(track=i),
                cover=track.cover or album.cover,
                parts=track.parts
            )

    @classmethod
    def from_track(cls, track: TrackType) -> Iterator[Self]:
        match track:
            case Single():
                yield from cls.from_single(track)
            case Split():
                yield from cls.from_split(track)
            case Playlist():
                yield from cls.from_playlist(track)
            case Merge():
                yield from cls.from_merge(track)

    @classmethod
    def from_single(cls, single: Single) -> Iterator[Self]:
        yield TrackData(
            metadata=Tags(**single.metadata.as_dict()),
            cover=single.cover,
            parts=[
                AudioData(url=single.url, start=single.start, end=single.end),
            ]
        )

    @classmethod
    def from_split(cls, split: Split) -> Iterator[Self]:
        end = TrackStub(metadata=TrackTags(title="unused"))
        tracks = itertools.chain(split.tracks, (end,))
        for track, next_track in itertools.pairwise(tracks):
            yield TrackData(
                metadata=Tags(**track.metadata.as_dict()),
                cover=track.cover or split.cover,
                parts=[
                    AudioData(
                        url=split.url,
                        start=track.start,
                        end=track.end or next_track.start,
                    ),
                ]
            )

    @classmethod
    def from_playlist(cls, playlist: Playlist) -> Iterator[Self]:
        i = 0
        for track in playlist.tracks:
            match track:
                case Drop():
                    i += 1
                case TrackStub():
                    yield track_data_from_track_stub(
                        track, playlist.url, i, playlist.cover
                    )
                    i += 1
                case MergeStub():
                    yield track_data_from_merge_stub(
                        track, playlist.url, i, playlist.cover,
                    )
                    i += len(track.parts)

    @classmethod
    def from_merge(cls, merge: Merge) -> Iterator[Self]:
        yield TrackData(
            metadata=Tags(**merge.metadata.as_dict()),
            cover=merge.cover,
            parts=[
                AudioData(url=part.url, start=part.start, end=part.end)
                for part in merge.parts
            ]
        )


def track_data_from_track_stub(
      track: TrackStub, url: str, i: int, playlist_cover: MaybeCover,
) -> TrackData:
    return TrackData(
        metadata=Tags(**track.metadata.as_dict()),
        cover=track.cover or playlist_cover,
        parts=[
            PlaylistAudioData(
                url=url, index=i, start=track.start, end=track.end,
            ),
        ]
    )


def track_data_from_merge_stub(
      track: MergeStub, url: str, i: int, playlist_cover: MaybeCover,
) -> TrackData:
    return TrackData(
        metadata=Tags(**track.metadata.as_dict()),
        cover=track.cover or playlist_cover,
        parts=[
            PlaylistAudioData(url=url, index=j, start=part.start, end=part.end)
            for j, part in enumerate(track.parts, start=i)
            if not isinstance(part, Drop)
        ]
    )
