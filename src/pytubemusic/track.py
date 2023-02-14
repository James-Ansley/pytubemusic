import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Self

from pytube import Playlist

from pytubemusic.audio import Audio
from pytubemusic.logutils import log_call
from pytubemusic.utils import (Pipe, get_cover, merge_metadata, pathify,
                               set_ends, thumbnail, to_delta)

__all__ = ["Track"]

STR_MAP = Mapping[str, Any]
TRACK_DATA = Iterable[STR_MAP]


@dataclass
class Track:
    raw_audio: Audio
    cover: NamedTemporaryFile
    start: timedelta
    end: timedelta
    metadata: STR_MAP

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

    @log_call(on_enter="Exporting '{self.metadata[title]}' to '{folder}'")
    def export(self, folder: Path = Path(".")):
        """
        Writes the track to folder / {track.title}.mp3

        Creates any dirs necessary in the folder path.
        Overwrites existing tracks with the same name.

        :param folder: The directory the track will be written to
        """
        os.makedirs(folder, exist_ok=True)
        with open(pathify(folder, self.title), "wb") as f:
            self.audio.export(f, self.metadata, self.cover.name)

    @classmethod
    @log_call(on_enter="Downloading '{metadata[album]}' from {url}")
    def from_album(
            cls,
            url: str,
            *,
            track_data: Iterable[Mapping[str, Any]],
            metadata: Mapping[str, str],
            cover_url: str = None,
    ) -> Iterable[Self]:
        """
        Factory that constructs an Album from a single video that contains
        multiple tracks in sequence.

        ``track_data`` is a list of string maps indicating track-specific
        data in the order of the tracks in the video and is of the form::

            [ { start: ..., [end: ...], metadata: { title: ..., ... } }, ... ]

        Where ``start`` and ``end`` (optional) are ``H?:M:S`` timestamps that
        indicate the start and end time stamps of the track and ``metadata``
        is a string map of track-specific FFMPEG MP3 metadata tags.

        :param url: The URL of the video
        :param track_data: A list of string maps of track data
        :param metadata: A String map of FFMPEG MP3 metadata tags
        :param cover_url: The url to a JPG cover image
        :return: an iterator of Track objects
        """
        audio = Audio.from_url(url)
        cover = thumbnail(url) if cover_url is None else get_cover(cover_url)
        track_data = (
            Pipe(track_data)
            .then(set_ends, audio.duration)
            .then(merge_metadata, metadata)
            .result
        )
        for track in track_data:
            yield cls(
                audio,
                cover,
                to_delta(track.get("start")),
                to_delta(track.get("end")),
                track["metadata"],
            )

    @classmethod
    @log_call(on_enter="Downloading '{metadata[title]}' from {url}")
    def from_video(
            cls,
            url: str,
            *,
            start: str = "00:00",
            end: str = None,
            metadata: Mapping[str, str],
            cover_url: str = None,
    ) -> Self:
        """
        Factory that constructs a Track from a video.

        :param url: The URL of the video
        :param metadata: A String map of FFMPEG MP3 metadata tags
        :param start: A H?:M:S.f? timestamp indicating the start time of the
            track. Defaults to 00:00:00.00
        :param end: A H?:M:S.f? timestamp indicating the end time of the track.
            Defaults to the length of the audio
        :param cover_url: The url to a JPG cover image
        :return: A new Track
        """
        audio = Audio.from_url(url)
        end = to_delta(end) if end is not None else audio.duration
        if cover_url is None:
            cover_url = thumbnail(url)
        else:
            cover_url = get_cover(cover_url)
        return cls(audio, cover_url, to_delta(start), end, metadata)

    @classmethod
    @log_call(on_enter="Downloading '{metadata[album]}' from {url}")
    def from_playlist(
            cls,
            url: str,
            *,
            track_data: Iterable[Mapping[str, Any]],
            metadata: Mapping[str, str],
            cover_url: str = None,
    ) -> Iterable[Self]:
        """
        Factory that constructs an Album from a playlist video that contains
        multiple tracks in sequence.

        :param url: The URL of the playlist
        :param track_data: A list of string maps of track data
        :param metadata: A String map of FFMPEG MP3 metadata tags
        :param cover_url: The url to a JPG cover image
        :return: an iterator of Track objects
        """
        playlist = Playlist(url)
        if track_data is None:
            track_data = [{} for _ in range(len(playlist))]
        video_data = zip(playlist.videos, track_data)
        for i, (video, data) in enumerate(video_data, start=1):
            track_metadata = data.pop("metadata") if "metadata" in data else {}
            yield cls.from_video(
                video.watch_url,
                metadata={
                    **metadata,
                    "track": i,
                    "title": video.title,
                    **track_metadata,
                },
                cover_url=cover_url,
                **data,
            )
