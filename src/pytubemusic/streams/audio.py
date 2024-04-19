from functools import reduce
from logging import ERROR
from operator import add
from typing import IO

from pydub import AudioSegment

from pytubemusic.model import *
from pytubemusic.streams import *
from pytubemusic.utils import *

__all__ = ("export_track",)


@panic_on_error(lambda err, _, track: f"An error occurred when exporting"
                                      f" track: {track.metadata.title}")
@on_enter(lambda _, track: f"Exporting track: {track.metadata.title}")
@on_exit(lambda r, _, track: f"Exported track: {track.metadata.title}")
@on_error(
    lambda err, _, track: f"Unable to export track "
                          f"`{track.metadata.title}`: {err}",
    level=ERROR,
)
def export_track(f: IO, track: TrackData) -> None:
    audio = reduce(add, (load_track_part(part) for part in track.track_parts))
    # cover cannot be inlined to prevent garbage collection of the named
    # file before export
    cover = load_cover(track)
    bitrate = get_bitrate(track)
    LOGGER.info(f"Writing to file: {track.metadata.title}")
    audio.export(
        f,
        format="mp3",
        tags=track.metadata.as_dict(),
        parameters=["-b:a", f"{bitrate}"],
        cover=cover.name
    )
    LOGGER.debug(f"Finished writing to file: {track.metadata.title}")


def load_track_part(track_part: AudioData | PlaylistAudioData) -> AudioSegment:
    match track_part:
        case AudioData(url, start, end):
            audio = get_audio_stream(url)
            return audio[to_milliseconds(start):to_milliseconds(end)]
        case PlaylistAudioData(url, index, start, end):
            playlist_urls = get_playlist_urls(url)
            audio = get_audio_stream(playlist_urls[index])
            return audio[to_milliseconds(start):to_milliseconds(end)]
        case _:
            never(track_part)


def to_milliseconds(maybe_timedelta: MaybeTimedelta) -> MaybeInt:
    if maybe_timedelta is not None:
        return int(maybe_timedelta.total_seconds() * 1000)
    else:
        return None


def load_cover(track: TrackData) -> "NamedTemporaryFile | None":
    if track.cover is None:
        return as_named_temp_file(load_uri(cover_photo_url(track)), ".jpg")
    else:
        return as_named_temp_file(load_uri(track.cover), ".jpg")
