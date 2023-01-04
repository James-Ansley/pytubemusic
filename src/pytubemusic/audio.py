import os
from collections.abc import Mapping
from datetime import datetime
from datetime import timedelta
from itertools import pairwise
from pathlib import PurePath
from tempfile import NamedTemporaryFile
from typing import Self

from pydub import AudioSegment
from pytube import Playlist, YouTube

from pytubemusic.logutils import log_call


class Album:
    def __init__(self, tracks: list["Track"], metadata: Mapping[str, str]):
        self.tracks = tracks
        self.metadata = metadata

    @classmethod
    @log_call(on_enter="Downloading '{metadata[album]}' from {url}")
    def from_url(
            cls,
            url: str,
            track_data: list[Mapping],
            metadata: Mapping[str, str],
    ) -> Self:
        audio = Audio.from_stream(url)
        track_data = Track.normalised_data(track_data, audio.duration.seconds)
        tracks = [Track.from_audio(audio, data) for data in track_data]
        return cls(tracks, metadata)

    @classmethod
    @log_call(on_enter="Downloading '{metadata[album]}' from {url}")
    def from_playlist(cls, url: str, metadata: Mapping[str, str]):
        playlist = Playlist(url)
        tracks = [
            Track.from_url(
                url=video.watch_url,
                metadata={"track": i, "title": video.title}
            )
            for i, video in enumerate(playlist.videos, start=1)
        ]
        return cls(tracks, metadata)

    @log_call(on_enter="Exporting album '{0.metadata[album]}'")
    def export(self, root: PurePath = PurePath(".")):
        root = root / self.metadata["album"]
        os.makedirs(root, exist_ok=True)
        for track in self.tracks:
            track.export(root, self.metadata)


class Track:
    def __init__(self, audio: "Audio", metadata: Mapping[str, str]):
        self._audio = audio
        self.metadata = metadata

    @classmethod
    @log_call(on_enter="Downloading '{metadata[title]}' from {url}")
    def from_url(
            cls,
            *,
            url: str,
            metadata: Mapping[str, str],
            start: int = None,
            end: int = None,
    ) -> Self:
        audio = Audio.from_stream(url).snip(start, end)
        return cls(audio, metadata)

    @classmethod
    def from_audio(cls, audio, track_data) -> Self:
        track_audio = audio.snip(track_data["start"], track_data["end"])
        return cls(track_audio, track_data["metadata"])

    @staticmethod
    def normalised_data(track_data: list[Mapping], end: int):
        track_data = track_data + [{"start": to_timestamp(end)}]
        for i, (t1, t2) in enumerate(pairwise(track_data), start=1):
            yield t1 | {
                "start": to_delta(t1["start"]),
                "end": to_delta(t1.get("end", t2["start"])),
                "metadata": {**t1.get("metadata", {}), "track": i},
            }

    @log_call(
        on_enter="Exporting track: {0.metadata[title]}")
    def export(self, root: PurePath = PurePath("."), metadata: Mapping = None):
        metadata = {} if metadata is None else metadata
        root = root / (self.metadata["title"].replace("/", "\u2044") + ".mp3")
        with open(root, "wb") as f:
            self._audio.export(f, metadata | self.metadata)


class Audio:
    def __init__(self, audio_data: AudioSegment, bitrate: int):
        self._audio_data = audio_data
        self.bitrate = bitrate

    @classmethod
    def from_stream(cls, url: str) -> Self:
        audio_file = NamedTemporaryFile("wb")
        raw_audio = YouTube(url).streams.get_audio_only()
        raw_audio.stream_to_buffer(audio_file)
        audio_data = AudioSegment.from_file(audio_file.name)
        return cls(audio_data, raw_audio.bitrate)

    def snip(self, start: int = None, end: int = None) -> Self:
        start = 0 if start is None else start
        end = self._audio_data.duration_seconds if end is None else end
        start, end = start * 1000, end * 1000
        return type(self)(self._audio_data[start:end], self.bitrate)

    @property
    def duration(self):
        return timedelta(seconds=self._audio_data.duration_seconds)

    def export(self, f, metadata):
        self._audio_data.export(
            f,
            format="mp3",
            tags=metadata,
            parameters=["-b:a", f"{self.bitrate}"]
        )


def to_delta(timestamp):
    template = "00:00:00"
    timestamp = template[:-len(timestamp)] + timestamp
    return (
            datetime.strptime(timestamp, "%H:%M:%S")
            - datetime.strptime(template, "%H:%M:%S")
    ).seconds


def to_timestamp(seconds):
    return f"{seconds // 3600}:{(seconds // 60) % 60}:{seconds % 60}"
