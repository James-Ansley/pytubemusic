import io
from collections.abc import Mapping
from datetime import timedelta
from typing import BinaryIO, Self

from pydub import AudioSegment
from pytube import YouTube

from pytubemusic.utils import to_microseconds

__all__ = ["Audio"]


class Audio:
    def __init__(self, audio_data: AudioSegment, bitrate: int):
        self._audio_data = audio_data
        self.bitrate = bitrate

    @property
    def duration(self) -> timedelta:
        """A timedelta of the Audio length"""
        return timedelta(seconds=self._audio_data.duration_seconds)

    def snip(self, start: timedelta = None, end: timedelta = None) -> Self:
        """
        Returns a new audio object clamped between the two timestamps start
        and end. Both default to the start and end of the audio respectively.
        """
        if start is None and end is None:
            return self
        start = 0 if start is None else to_microseconds(start)
        end = to_microseconds(self.duration if end is None else end)
        return type(self)(self._audio_data[start:end], self.bitrate)

    def export(self, f: BinaryIO, metadata: Mapping[str, str], cover=None):
        """
        Writes the audio to the given BinaryIO in MP3 format with the given
        metadata.
        """
        self._audio_data.export(
            f,
            format="mp3",
            tags=metadata,
            parameters=["-b:a", f"{self.bitrate}"],
            cover=cover,
        )

    @classmethod
    def from_url(cls, url: str) -> Self:
        """
        Downloads audio from the video associated with the URL

        :param url: The video URL
        :return: An Audio object
        """
        buffer = io.BytesIO()
        raw_audio = YouTube(url).streams.get_audio_only()
        raw_audio.stream_to_buffer(buffer)
        buffer.seek(0)
        audio_data = AudioSegment.from_file(buffer)
        return cls(audio_data, raw_audio.bitrate)
