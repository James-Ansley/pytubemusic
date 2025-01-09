import functools
from io import BytesIO
from typing import IO

from pydub import AudioSegment
from pytubefix import Playlist, YouTube

from pytubemusic.model.track import AudioData, PlaylistAudioData
from .utils import stream
from ..logging import log
from ..model.audio import RawAudio


def fetch_audio_data(audio_data: AudioData | PlaylistAudioData) -> RawAudio:
    url = fetch_video_url(audio_data)
    log(f"Processing audio from: {url}")
    buffer, bitrate = audio(url)
    return RawAudio(
        segment=AudioSegment.from_file(
            buffer,
            start_second=audio_data.start_second(),
            duration=audio_data.duration_seconds(),
        ),
        bit_rate=bitrate,
    )


def audio(url: str) -> tuple[IO, int]:
    buffer, bitrate = _cached_audio_helper(url)
    return BytesIO(buffer), bitrate


@functools.lru_cache(maxsize=1)
def _cached_audio_helper(url: str) -> tuple[bytes, int]:
    log(f"Fetching audio from: {url}")
    with stream(BytesIO()) as buffer:
        raw_audio = YouTube(url).streams.get_audio_only()
        raw_audio.stream_to_buffer(buffer)
    return buffer.read(), raw_audio.bitrate


def fetch_video_url(audio_data: AudioData | PlaylistAudioData) -> str:
    match audio_data:
        case AudioData(url):
            return url
        case PlaylistAudioData(url, index):
            return fetch_playlist_video_url(url, index)


def fetch_playlist_video_url(playlist_url: str, index: int) -> str:
    return Playlist(playlist_url).video_urls[index]
