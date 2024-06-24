import importlib
from datetime import timedelta
from typing import IO

import pytest
from pydub import AudioSegment

import pytubemusic
from pytubemusic.model.audio import RawAudio
from pytubemusic.model.track import AudioData, PlaylistAudioData
from pytubemusic.streams.audio import fetch_audio_data
from tests import test


class MockAudioStream:
    def __init__(self):
        self.bitrate = 1

    def stream_to_buffer(self, buffer: IO):
        buffer.write(b"Some audio data")


class MockStreamQuery:
    def get_audio_only(self):
        return MockAudioStream()


class MockYoutube:
    url: str = None

    def __init__(self, url):
        MockYoutube.url = url
        self.streams = MockStreamQuery()


class MockPlaylist:
    url: str = None

    def __init__(self, url):
        MockYoutube.url = url
        self.video_urls = [None, url + "at_index_1"]


# noinspection PyMissingConstructor,PyMethodOverriding
class MockAudioSegment(AudioSegment):
    def __init__(self, value, start, duration):
        self.value = value
        self.start_second = start
        self.duration = duration

    @classmethod
    def from_file(cls, buffer: IO, start_second, duration):
        return MockAudioSegment(
            buffer.read().decode(),
            start_second,
            duration,
        )


@pytest.fixture(autouse=True)
def patch_youtube_and_audio(monkeypatch):
    monkeypatch.setattr("pytube.YouTube", MockYoutube)
    monkeypatch.setattr("pytube.Playlist", MockPlaylist)
    monkeypatch.setattr("pydub.AudioSegment", MockAudioSegment)
    # Reload pytubemusic modules to re-import patched modules
    importlib.reload(pytubemusic.model.track)
    importlib.reload(pytubemusic.streams.audio)


# noinspection PyTypeChecker
@test()
def audio_data_can_be_fetched_from_audio_data():
    audio = AudioData(
        url="www.example.com/watch?v=",
        start=timedelta(seconds=1),
        end=timedelta(minutes=1, seconds=5),
    )
    raw_audio: RawAudio = fetch_audio_data(audio)
    segment: MockAudioSegment = raw_audio.segment
    assert MockYoutube.url == audio.url
    assert segment.value == "Some audio data"
    assert segment.start_second == 1
    assert segment.duration == 64


# noinspection PyTypeChecker
@test()
def audio_data_can_be_fetched_from_playlist_audio_data():
    audio = PlaylistAudioData(
        url="www.example.com/watch?v=",
        index=1,
        start=timedelta(seconds=1),
        end=timedelta(minutes=1, seconds=5),
    )
    segment: MockAudioSegment = fetch_audio_data(audio)
    assert MockYoutube.url == audio.url + "at_index_1"
    assert segment.segment.value == "Some audio data"
    assert segment.segment.start_second == 1
    assert segment.segment.duration == 64
