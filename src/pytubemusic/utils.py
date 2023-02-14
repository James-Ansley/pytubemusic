import urllib.request
from collections.abc import Iterable, Iterator, Mapping
from datetime import datetime, timedelta
from itertools import chain, pairwise
from pathlib import PurePath
from tempfile import NamedTemporaryFile
from typing import Any, Self

from pytube import YouTube

STR_MAP = Mapping[str, Any]
TRACK_DATA = Iterable[STR_MAP]


def to_delta(timestamp: str) -> timedelta:
    """Converts a H?:M:S.f? timestamp string to a timedelta"""
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


class Pipe:
    def __init__(self, data):
        """Allows for piped operations to the data via method chaining"""
        self.result = data

    def then(self, func, *args, **kwargs) -> Self:
        self.result = func(self.result, *args, **kwargs)
        return self


def make_track_data(
        track_data: list[Mapping],
        end: timedelta,
) -> Iterator[Mapping]:
    """
    Adds track number metadata to a list of track data and ensures tracks have
    start and end timestamps

    :param track_data: A list of string maps of incomplete track data
    :param end: The length of the Album in seconds
    :return: Yields string maps of track data
    """
    track_data = track_data + [{"start": to_timestamp(end)}]
    for i, (t1, t2) in enumerate(pairwise(track_data), start=1):
        yield t1 | {
            "start": t1["start"],
            "end": t1.get("end", t2["start"]),
            "metadata": {"track": i} | t1.get("metadata", {}),
        }


def set_ends(track_data: TRACK_DATA, end: timedelta) -> TRACK_DATA:
    """
    Fills in missing "end" timestamps setting them to the start of the next
    track. Returns a new mapping of track data.
    """
    track_data = chain(track_data, [{"start": to_timestamp(end)}])
    for i, (t1, t2) in enumerate(pairwise(track_data), start=1):
        yield t1 | {
            "start": t1["start"],
            "end": t1.get("end", t2["start"]),
            "metadata": {"track": i, **t1.get("metadata", {})},
        }


def merge_metadata(track_data: TRACK_DATA, metadata: STR_MAP) -> TRACK_DATA:
    """
    Merges any album metadata with track-specific metadata.
    Track metadata overrides album metadata.
    """
    for data in track_data:
        yield {**data, "metadata": {**metadata, **data["metadata"]}}


def thumbnail(url) -> NamedTemporaryFile:
    """Returns a default cover – the video's thumbnail"""
    thumbnail_url = YouTube(url).thumbnail_url
    return get_cover(thumbnail_url)


def get_cover(url) -> NamedTemporaryFile:
    """Downloads an image into a named temporary file to be used as cover art"""
    f = NamedTemporaryFile(suffix='.jpg')
    img = urllib.request.urlopen(url).read()
    f.write(img)
    return f
