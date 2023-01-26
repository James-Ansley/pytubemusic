import io
import os
from collections.abc import Mapping
from datetime import timedelta
from pathlib import PurePath
from typing import BinaryIO, Self

from pydub import AudioSegment
from pytube import Playlist, YouTube

from pytubemusic._utils import make_track_data, to_delta
from pytubemusic.logutils import log_call


class Album:
    def __init__(self, tracks: list["Track"], metadata: Mapping[str, str]):
        self.tracks = tracks
        self.metadata = metadata

    @classmethod
    @log_call(on_enter="Downloading '{metadata[album]}' from {url}")
    def from_video(
            cls,
            url: str,
            track_data: list[Mapping],
            metadata: Mapping[str, str],
    ) -> Self:
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
        :return: A new Album
        """
        audio = Audio.from_url(url)
        track_data = make_track_data(track_data, audio.duration)
        tracks = [Track.from_audio(audio, data) for data in track_data]
        return cls(tracks, metadata)

    @classmethod
    @log_call(on_enter="Downloading '{metadata[album]}' from {url}")
    def from_playlist(cls, url: str, metadata: Mapping[str, str]):
        """
        Factory that constructs an Album from a playlist video that contains
        multiple tracks in sequence.

        :param url: The URL of the playlist
        :param metadata: A String map of FFMPEG MP3 metadata tags
        :return: A new Album
        """
        playlist = Playlist(url)
        tracks = [
            Track.from_video(
                url=video.watch_url,
                metadata={"track": i, "title": video.title}
            )
            for i, video in enumerate(playlist.videos, start=1)
        ]
        return cls(tracks, metadata)

    @log_call(on_enter="Exporting album '{self.metadata[album]}'")
    def export(self, root: PurePath = PurePath(".")):
        """
        Writes album tracks to files contained in a directory. The directory
        will have the album name as a title.

        :param root: The directory to write the album directory to.
        """
        root = root / self.metadata["album"]
        os.makedirs(root, exist_ok=True)
        for track in self.tracks:
            track.export(root, self.metadata)


class Track:
    def __init__(self, audio: "Audio", metadata: Mapping[str, str], ):
        self._audio = audio
        self.metadata = metadata

    @classmethod
    @log_call(on_enter="Downloading '{metadata[title]}' from {url}")
    def from_video(
            cls,
            url: str,
            metadata: Mapping[str, str],
            start: str = None,
            end: str = None,
    ) -> Self:
        """
        Factory that constructs a Track from a video.

        :param url: The URL of the playlist
        :param metadata: A String map of FFMPEG MP3 metadata tags
        :param start: A H?:M:S timestamp indicating the start time of the track.
            Defaults to 00:00:00
        :param end: A H?:M:S timestamp indicating the end time of the track.
            Defaults to the length of the audio
        :return: A new Track
        """
        audio = Audio.from_url(url).snip(start, end)
        return cls(audio, metadata)

    @classmethod
    def from_audio(cls, audio: "Audio", track_data: Mapping) -> Self:
        """
        Factory that constructs a Track from a larger Audio object.

        ``track_data`` is of the form::

            { [start = ...], [end = ...], metadata = {title: ..., ...} }

        Where start and end are optional H?:M:S timestamps and metadata is a
        string map of track-specific FFMPEG MP3 metadata tags.

        :param audio: The audio object to extract the track from
        :param track_data: A string map of track data
        :return: A Track
        """
        track_audio = audio.snip(track_data.get("start"), track_data.get("end"))
        return cls(track_audio, track_data["metadata"])

    @log_call(on_enter="Exporting track: {self.metadata[title]}")
    def export(self, root: PurePath = PurePath("."), metadata: Mapping = None):
        """
        Writes the track to a file in the directory specified by ``root``.

        :param root: The directory to write the file to
        :param metadata: Track metadata to include. Defaults to {}
        """
        metadata = {} if metadata is None else metadata
        root = root / (self.metadata["title"].replace("/", "\u2044") + ".mp3")
        with open(root, "wb") as f:
            self._audio.export(f, metadata | self.metadata)


class Audio:
    def __init__(self, audio_data: AudioSegment, bitrate: int):
        self._audio_data = audio_data
        self.bitrate = bitrate

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

    def snip(self, start: str = None, end: str = None) -> Self:
        """
        Returns a new audio object clamped between the two timestamps start
        and end. Both default to the start and end of the audio respectively.
        """
        if start is None and end is None:
            return self
        start = 0 if start is None else to_delta(start).seconds * 1000
        end = (self.duration if end is None else to_delta(end)).seconds * 1000
        return type(self)(self._audio_data[start:end], self.bitrate)

    @property
    def duration(self) -> timedelta:
        """A timedelta of the Audio length"""
        return timedelta(seconds=self._audio_data.duration_seconds)

    def export(self, f: BinaryIO, metadata: Mapping[str, str]):
        """
        Writes the audio to the given BinaryIO in MP3 format with the given
        metadata.
        """
        self._audio_data.export(
            f,
            format="mp3",
            tags=metadata,
            parameters=["-b:a", f"{self.bitrate}"],
        )
