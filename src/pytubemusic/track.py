import os
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Self

from pipe_utils.override import *
from pytube import Playlist

from pytubemusic.audio import Audio
from pytubemusic.logutils import log_call, log_iter
from pytubemusic.utils import *

__all__ = ["Track"]

from pytubemusic.utils import File


@dataclass
class Track:
    raw_audio: Audio
    metadata: StrMap
    cover: File = None
    start: timedelta | None = None
    end: timedelta | None = None

    def __post_init__(self):
        self.start = to_delta(self.start)
        self.end = to_delta(self.end)

    @property
    def audio(self) -> Audio:
        """The raw audio snipped to the track start and end times"""
        return self.raw_audio.snip(self.start, self.end)

    @property
    def title(self) -> str:
        """The track title"""
        return self.metadata["title"]

    @property
    def album(self) -> str | None:
        """The track album – May be None"""
        return self.metadata.get("album")

    @log_call(on_enter="Exporting `{self.metadata[title]}` to `{folder}`")
    def export(self, folder: Path = Path(".")):
        """
        Writes the track to folder / {track.title}.mp3

        Creates any dirs necessary in the folder path.
        Overwrites existing tracks with the same name.

        :param folder: The directory the track will be written to
        """
        os.makedirs(folder, exist_ok=True)
        with open(pathify(folder, self.title), "wb") as f:
            self.audio.export(f, self.metadata, self.cover)

    @classmethod
    @log_call(on_enter="Downloading album `{metadata[album]}`")
    def from_album(
            cls, tracks: TrackData, metadata: StrMap, cover: Mapping, **kwargs,
    ) -> Iterable[Self]:
        return (
                Pipe(tracks)
                | flat_map(lambda data: cls.track_parts(cover=cover, **data))
                | map_indexed(lambda i, t:
                              with_metadata(t, i, metadata), start=1)
        ).get()

    @classmethod
    def track_parts(cls, type: str, **kwargs) -> Iterator[Mapping]:
        match type:
            case "track":
                yield cls.from_track_part(**kwargs)
            case "merge":
                yield cls.from_merge_part(**kwargs)
            case "split":
                yield from cls.from_split_part(**kwargs)
            case "playlist":
                if kwargs.get("join", False):
                    yield cls.from_playlist_part_to_track(**kwargs)
                else:
                    yield from cls.from_playlist_part_to_multi(**kwargs)
            case _:
                raise ValueError(f"Unsupported track part type: `{type}`")

    @classmethod
    @log_call(on_enter="Downloading track `{metadata[title]}` from: {url}")
    def from_track_part(
            cls,
            url: str,
            metadata: StrMap,
            cover: File,
            start: str = None,
            end: str = None,
            **kwargs,
    ) -> Self:
        return cls(
            raw_audio=Audio.from_url(url),
            metadata=metadata,
            cover=cover,
            start=start,
            end=end,
        )

    @classmethod
    @log_call(on_enter="Downloading multi track `{metadata[title]}`")
    def from_merge_part(
            cls, tracks: TrackData, metadata: StrMap, cover: File, **kwargs,
    ) -> Self:
        segments = []
        log = log_iter(on_each="Downloading part {i} from: {0[url]}", start=1)
        for track in log(tracks):
            start = to_delta(track.get("start"))
            end = to_delta(track.get("end"))
            segments.append(Audio.from_url(track["url"]).snip(start, end))
        return cls(
            raw_audio=Audio.join(segments), metadata=metadata, cover=cover,
        )

    @classmethod
    @log_call(on_enter="Downloading split track from: {url}")
    def from_split_part(
            cls, url: str, tracks: TrackData, cover: File, **kwargs,
    ) -> Iterable[Self]:
        audio = Audio.from_url(url)
        tracks = set_ends(tracks)
        for track in tracks:
            yield cls(
                raw_audio=audio,
                cover=cover,
                metadata=track["metadata"],
                start=track.get("start"),
                end=track.get("end"),
            )

    @classmethod
    @log_call(on_enter="Downloading playlist as track from: {url}")
    def from_playlist_part_to_track(
            cls, url: str, tracks: TrackData, metadata: StrMap, cover: File,
            **kwargs,
    ) -> Self:
        urls = Playlist(url).video_urls
        tracks = pad(tracks, dict, len(urls))
        data = [track | {"url": url} for url, track in zip(urls, tracks)
                if not track.get("drop", False)]
        return cls.from_merge_part(data, metadata, cover)

    @classmethod
    @log_call(on_enter="Downloading playlist from: {url}")
    def from_playlist_part_to_multi(
            cls, url: str, tracks: TrackData, cover: File, **kwargs,
    ) -> Iterator[Self]:
        urls = Playlist(url).video_urls
        tracks = pad(tracks, dict, len(urls))
        for url, track in zip(urls, tracks):
            if not track.get("drop", False):
                data = track | {"url": url, "cover": cover}
                yield cls.from_track_part(**data)


def with_metadata(track: Track, index: int, metadata: StrMap) -> Track:
    return Track(
        raw_audio=track.raw_audio,
        metadata={**metadata, "track": index, **track.metadata},
        cover=track.cover,
        start=track.start,
        end=track.end,
    )
