from datetime import datetime, timedelta
from itertools import pairwise
from typing import Iterator, Mapping


def to_delta(timestamp: str) -> timedelta:
    """Converts a H?:M:S timestamp string to a timedelta"""
    template = "00:00:00"
    timestamp = template[:-len(timestamp)] + timestamp
    return (
            datetime.strptime(timestamp, "%H:%M:%S")
            - datetime.strptime(template, "%H:%M:%S")
    )


def to_timestamp(delta: timedelta) -> str:
    """Converts a timedelta to a H:M:S timestamp string"""
    return (
        f"{delta.seconds // 3600:02d}"
        f":{(delta.seconds // 60) % 60:02d}"
        f":{delta.seconds % 60:02d}"
    )


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
            "metadata": {**t1.get("metadata", {}), "track": i},
        }
