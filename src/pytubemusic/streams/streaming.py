from contextlib import AbstractContextManager, contextmanager
from functools import cache
from io import BytesIO
from logging import DEBUG, ERROR
from tempfile import NamedTemporaryFile
from typing import IO
from urllib.error import URLError
from urllib.request import urlopen

from pydub import AudioSegment
from pytube import Playlist, YouTube
from pytube.exceptions import PytubeError

from pytubemusic.model import AudioData, MaybeStr, PlaylistAudioData, TrackData
from pytubemusic.utils import on_enter, on_error, on_exit, panic_on_error

__all__ = (
    "get_audio_stream",
    "get_playlist_urls",
    "load_uri",
    "get_bitrate",
    "cover_photo_url",
    "as_named_temp_file",
)


@cache
@panic_on_error(
    lambda err, track: f"An error occurred when fetching bitrate "
                       f"for `{track.metadata.title}`",
    catch=PytubeError,
)
@on_enter(lambda track: f"Fetching bitrate: {track.metadata.title}")
@on_exit(lambda _, track: f"Fetched bitrate: {track.metadata.title}",
         level=DEBUG)
@on_error(
    lambda err, track: f"Unable to fetch bitrate for "
                       f"`{track.metadata.title}`: {err}",
    catch=PytubeError,
    level=ERROR,
)
def get_bitrate(track: TrackData) -> int:
    part = track.track_parts[0]
    match part:
        case AudioData(url):
            return YouTube(url).streams.get_audio_only().bitrate
        case PlaylistAudioData(url, index):
            return YouTube(
                get_playlist_urls(url)[index]
            ).streams.get_audio_only().bitrate


@cache
@panic_on_error(
    lambda err, url: f"An error occurred when fetching `{url}`",
    catch=PytubeError,
)
@on_enter(lambda url: f"Fetching audio: {url}")
@on_exit(lambda _, url: f"Fetched audio: {url}", level=DEBUG)
@on_error(
    lambda err, url: f"Unable to fetch `{url}`: {err}",
    catch=PytubeError,
    level=ERROR,
)
def get_audio_stream(url: str) -> AudioSegment:
    with stream(BytesIO()) as buffer:
        raw_audio = YouTube(url).streams.get_audio_only()
        raw_audio.stream_to_buffer(buffer)
    return AudioSegment.from_file(buffer)


@cache
@panic_on_error(
    lambda err, url: f"An error occurred when fetching playlist URLs `{url}`",
    catch=(PytubeError, KeyError),
)
@on_enter(lambda url: f"Fetching Playlist URLs: {url}")
@on_exit(lambda _, url: f"Fetched Playlist URLs: {url}", level=DEBUG)
@on_error(
    lambda err, url: f"Unable to fetch playlist URLs from `{url}`: {err}",
    catch=(PytubeError, KeyError),
    level=ERROR,
)
def get_playlist_urls(url: str) -> tuple[str]:
    return tuple(Playlist(url).video_urls)


@cache
@panic_on_error(
    lambda err, uri: f"An error occurred when retrieving the "
                     f"resource at the following uri: `{uri}`"
)
@on_enter(lambda uri: f"Retrieving resource: {uri}")
@on_exit(lambda _, uri: f"Retrieved resource: {uri}", level=DEBUG)
@on_error(
    lambda err, uri: f"Unable to retrieve resource specified by uri "
                     f"`{uri}`: {err}",
    catch=URLError,
    level=ERROR,
)
def load_uri(uri: str) -> bytes:
    with urlopen(uri) as f:
        return f.read()


@cache
@panic_on_error(
    lambda err, track: f"An error occurred when retrieving the "
                       f"cover photo for at the following track: "
                       f"`{track.metadata.title}`"
)
@on_enter(lambda track: f"Retrieving cover photo for: {track.metadata.title}")
@on_exit(
    lambda _, track: f"Retrieved cover phoro: {track.metadata.title}",
    level=DEBUG,
)
@on_error(
    lambda err, track: f"Unable to retrieve cover photo "
                       f"for `{track.metadata.title}`: {err}",
    catch=URLError,
    level=ERROR,
)
def cover_photo_url(track: TrackData) -> str:
    part = track.track_parts[0]
    match part:
        case AudioData(url):
            return YouTube(url).thumbnail_url
        case PlaylistAudioData(url):
            return (
                Playlist(url)
                .sidebar_info
                [0]
                ["playlistSidebarPrimaryInfoRenderer"]
                ["thumbnailRenderer"]
                ["playlistCustomThumbnailRenderer"]
                ["thumbnail"]
                ["thumbnails"]
                [-1]
                ["url"]
            )


def as_named_temp_file(data: bytes, ext: MaybeStr = None) -> NamedTemporaryFile:
    f = NamedTemporaryFile("wb", suffix=ext)
    f.write(data)
    return f


@contextmanager
def stream[T: IO](buff: T) -> AbstractContextManager[T]:
    try:
        yield buff
    finally:
        buff.seek(0)
