import os
from itertools import pairwise
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Self

from dateutil.parser import parse
from pydub import AudioSegment
from pytube import YouTube

from pytubemusic.logutils import log_call


class Audio:
    def __init__(self, audio_data: AudioSegment, bitrate: int, metadata: dict):
        self._audio_data = audio_data
        self.bitrate = bitrate
        self.metadata = metadata

    @classmethod
    @log_call(on_enter="Downloading Audio \"{metadata[name]}\" from {url}")
    def from_url(cls, *, url, metadata) -> Self:
        audio_file = NamedTemporaryFile("wb")
        raw_audio = YouTube(url).streams.get_audio_only()
        raw_audio.stream_to_buffer(audio_file)
        audio_data = AudioSegment.from_file(audio_file.name)
        return cls(audio_data, raw_audio.bitrate, metadata)

    @property
    def microseconds(self) -> int:
        return self._audio_data.duration_seconds * 1000

    @log_call(on_enter="Splitting \"{0.metadata[name]}\" to Tracks")
    def split_to_tracks(self):
        tracks = self._tracks_with_timestamp_ranges()
        self.metadata.pop("tracks")
        new_tracks = []
        for i, track in enumerate(tracks, start=1):
            new_tracks.append(
                Audio(
                    self._audio_data[track["from"]:track["to"]],
                    self.bitrate,
                    self.metadata | {
                        "track": f"{i}/{len(tracks)}",
                        "name": track["name"],
                    },
                )
            )
        return new_tracks

    @log_call(on_enter="Writing {0.metadata[name]}")
    def export(self, out: Path = None):
        if out is None:
            out = Path(self.metadata["album"])
        os.makedirs(out, exist_ok=True)
        track_file = out / (self.metadata["name"] + ".mp3")
        with open(track_file, "wb") as f:
            self._audio_data.export(
                f,
                format="mp3",
                tags=self.metadata,
                parameters=["-b:a", f"{self.bitrate}"]
            )

    def _tracks_with_timestamp_ranges(self):
        tracks = self.metadata["tracks"]
        tracks = [{**t, "time": to_delta(t["time"])} for t in tracks]
        times = pairwise((*(t["time"] for t in tracks), self.microseconds))
        return [{**track, "from": t1, "to": t2}
                for track, (t1, t2) in zip(tracks, times)]


def to_delta(timestamp):
    template = "00:00:00"
    timestamp = template[:-len(timestamp)] + timestamp
    return (parse(timestamp) - parse(template)).seconds * 1000
