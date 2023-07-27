import contextlib
import urllib.request
from collections.abc import Iterable, Mapping
from datetime import datetime, timedelta
from itertools import chain, pairwise
from pathlib import Path, PurePath
from tempfile import NamedTemporaryFile
from typing import Any

from pytubemusic.logutils import PanicOn

__all__ = [
    "to_delta", "to_timestamp", "to_microseconds", "pathify",
    "set_ends", "merge_metadata", "get_cover", "pad", "File", "TrackData",
    "StrMap", "open_or_panic",
]

StrMap = Mapping[str, Any]
TrackData = Iterable[StrMap]

File = NamedTemporaryFile


def to_delta(timestamp: str | timedelta | None) -> timedelta | None:
    """Converts a H?:M:S.f? timestamp string to a timedelta"""
    if timestamp is None:
        return None
    elif isinstance(timestamp, timedelta):
        return timestamp

    if "." in timestamp:
        timestamp, microseconds = timestamp.split(".")
    else:
        microseconds = "00"
    template = "00:00:00"
    timestamp = template[:-len(timestamp)] + timestamp + "." + microseconds
    return (
            datetime.strptime(timestamp, "%H:%M:%S.%f")
            - datetime.strptime(template, "%H:%M:%S")
    )


def to_timestamp(delta: timedelta) -> str:
    """Converts a timedelta to a H:M:S.f timestamp string"""
    return (
        f"{int(delta.total_seconds() // 3600):02.0f}"
        f":{int(delta.total_seconds() // 60) % 60:02.0f}"
        f":{int(delta.total_seconds() % 60):02.0f}"
        f".{(delta.total_seconds() % 1) * 100:02.0f}"
    )


def to_microseconds(delta: timedelta) -> int:
    """Coverts a time delta to total_microseconds"""
    return int(delta.total_seconds() * 1000)


def pathify(root: PurePath, title: str, ext=".mp3") -> PurePath:
    """
    Replaces invalid characters in filenames and joins the params to a path
    with the given extension
    """
    return root / (title.replace("/", "\u2044") + ext)


def set_ends(track_data: TrackData) -> TrackData:
    """
    Fills in missing "end" timestamps setting them to the start of the next
    track. Returns a new mapping of track data.
    """
    for t1, t2 in pairwise(chain(track_data, [{"start": None}])):
        yield t1 | {
            "start": t1.get("start"),
            "end": t1.get("end", t2["start"]),
        }


def merge_metadata(track_data: TrackData, metadata: StrMap) -> TrackData:
    """
    Merges any album metadata with track-specific metadata.
    Track metadata overrides album metadata.
    """
    for data in track_data:
        yield {**data, "metadata": {**metadata, **data["metadata"]}}


def get_cover(cover, relative_to: Path) -> "None | NamedTemporaryFile":
    """Downloads an image into a named temporary file to be used as cover art"""
    match cover:
        case {"url": url}:
            f = NamedTemporaryFile(suffix='.jpg')
            img = urllib.request.urlopen(url).read()
            f.write(img)
            return f
        case {"file": path}:
            tmp = NamedTemporaryFile(suffix='.jpg')
            msg = f"Cannot find cover file"
            with open_or_panic(relative_to.parent / path, "rb", msg) as f:
                tmp.write(f.read())
            return tmp
        case None:
            return None
        case _:
            raise ValueError(f"Unrecognised Cover format: `{cover}`")


def pad(tracks, factory, length):
    tracks = list(tracks)
    tracks += [factory() for _ in range(length - len(tracks))]
    return tracks


@contextlib.contextmanager
def open_or_panic(file_name, mode, msg):
    with (PanicOn(OSError, msg), open(file_name, mode) as f):
        yield f
