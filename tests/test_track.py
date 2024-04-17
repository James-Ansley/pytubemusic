from datetime import timedelta

from pydantic import ValidationError
from pytest import raises

from pytubemusic.model import *
from tests.utils import test


@test
def a_single_can_be_created_with_minimal_data():
    single = Single(
        **{"url": "www.example.com", "metadata": {"title": "A Title"}}
    )
    expect = Single(url="www.example.com", metadata=TrackTags(title="A Title"))
    assert single == expect


@test
def a_single_can_be_created_with_full_data():
    single = Single(**{
        "url": "www.example.com",
        "metadata": {"title": "A Title"},
        "cover": {"path": "./cover.jpg"},
        "start": "00:00:01",
        "end": "00:07:02",
    })
    expect = Single(
        url="www.example.com",
        metadata=TrackTags(title="A Title"),
        cover=File(path="./cover.jpg"),
        start=timedelta(seconds=1),
        end=timedelta(minutes=7, seconds=2),
    )
    assert single == expect


@test
def split_tracks_cannot_be_created_with_zero_tracks():
    with raises(ValidationError):
        Split(url="www.example.com", tracks=())
    Split(
        url="www.example.com",
        tracks=(TrackStub(metadata=TrackTags(title="Title")),),
    )


@test
def a_split_track_can_be_created_with_minimal_data():
    split = Split(**{
        "url": "www.example.com",
        "tracks": [{"metadata": {"title": "My Title"}}],
    })
    expect = Split(
        url="www.example.com",
        tracks=(TrackStub(metadata=TrackTags(title="My Title")),)
    )
    assert split == expect


@test
def a_split_track_can_be_created_with_full_data():
    split = Split(**{
        "url": "www.example.com",
        "cover": {"href": "www.example.com/pic.jpeg"},
        "tracks": [
            {
                "metadata": {"title": "My Title 1"},
                "start": "00:00:01",
                "end": "00:01:23",
            },
            {
                "metadata": {"title": "My Title 2"},
                "start": "00:04:56",
                "end": "00:05:55",
            },
            {
                "metadata": {"title": "My Title 3"},
                "start": "00:05:56",
                "end": "00:10:10",
            },
        ]
    })
    expect = Split(
        url="www.example.com",
        cover=Url(href="www.example.com/pic.jpeg"),
        tracks=(
            TrackStub(
                metadata=TrackTags(title="My Title 1"),
                start=timedelta(seconds=1),
                end=timedelta(minutes=1, seconds=23),
            ),
            TrackStub(
                metadata=TrackTags(title="My Title 2"),
                start=timedelta(minutes=4, seconds=56),
                end=timedelta(minutes=5, seconds=55),
            ),
            TrackStub(
                metadata=TrackTags(title="My Title 3"),
                start=timedelta(minutes=5, seconds=56),
                end=timedelta(minutes=10, seconds=10),
            ),
        )
    )
    assert split == expect


@test
def a_playlist_can_be_created_with_minimal_data():
    playlist = Playlist(**{"url": "www.example.com"})
    assert playlist == Playlist(url="www.example.com")


@test
def a_playlist_can_be_created_with_full_data():
    playlist = Playlist(**{
        "url": "www.example.com",
        "cover": {"href": "www.example.com/pic.jpeg"},
        "tracks": (
            {
                "metadata": {"title": "My Title 1"},
                "start": "00:00:01",
                "end": "00:01:23",
            },
            "DROP",
            {
                "metadata": {"title": "My Title 3"},
                "start": "00:05:56",
                "end": "00:10:10",
            },
        )
    })
    expect = Playlist(
        url="www.example.com",
        cover=Url(href="www.example.com/pic.jpeg"),
        tracks=(
            TrackStub(
                metadata=TrackTags(title="My Title 1"),
                start=timedelta(seconds=1),
                end=timedelta(minutes=1, seconds=23),
            ),
            "DROP",
            TrackStub(
                metadata=TrackTags(title="My Title 3"),
                start=timedelta(minutes=5, seconds=56),
                end=timedelta(minutes=10, seconds=10),
            ),
        )
    )
    assert playlist == expect


@test
def a_merge_playlist_can_be_created_with_minimal_data():
    playlist = MergePlaylist(**{
        "url": "www.example.com", "metadata": {"title": "Foo"},
    })
    expect = MergePlaylist(
        url="www.example.com",
        metadata=TrackTags(title="Foo"),
    )
    assert playlist == expect


@test
def a_merge_playlist_can_be_created_with_full_data():
    playlist = MergePlaylist(**{
        "url": "www.example.com",
        "metadata": {"title": "My Track"},
        "cover": {"href": "www.example.com/pic.jpeg"},
        "tracks": (
            {"start": "00:00:01", "end": "00:01:23"},
            "DROP",
            {"start": "00:05:56", "end": "00:10:10"},
        )
    })
    expect = MergePlaylist(
        url="www.example.com",
        metadata=TrackTags(title="My Track"),
        cover=Url(href="www.example.com/pic.jpeg"),
        tracks=(
            TimeStub(
                start=timedelta(seconds=1),
                end=timedelta(minutes=1, seconds=23),
            ),
            "DROP",
            TimeStub(
                start=timedelta(minutes=5, seconds=56),
                end=timedelta(minutes=10, seconds=10),
            ),
        )
    )
    assert playlist == expect


@test
def a_merge_can_be_created_with_minimal_data():
    merge = Merge(**{
        "metadata": {"title": "Merged"},
        "tracks": ({"url": "www.example.com"},)
    })
    expect = Merge(
        metadata=TrackTags(title="Merged"),
        tracks=(AudioStub(url="www.example.com"),),
    )
    assert merge == expect


@test
def a_merge_can_be_created_with_full_data():
    merge = Merge(**{
        "metadata": {"title": "Merged"},
        "tracks": (
            {
                "url": "www.example.com/1",
                "start": "00:00:01",
                "end": "00:01:23",
            },
            {
                "url": "www.example.com/2",
                "start": "00:04:56",
                "end": "00:05:55",
            },
            {
                "url": "www.example.com/3",
                "start": "00:05:56",
                "end": "00:10:10",
            },
        )
    })
    expect = Merge(
        metadata=TrackTags(title="Merged"),
        tracks=(
            AudioStub(
                url="www.example.com/1",
                start=timedelta(seconds=1),
                end=timedelta(minutes=1, seconds=23),
            ),
            AudioStub(
                url="www.example.com/2",
                start=timedelta(minutes=4, seconds=56),
                end=timedelta(minutes=5, seconds=55),
            ),
            AudioStub(
                url="www.example.com/3",
                start=timedelta(minutes=5, seconds=56),
                end=timedelta(minutes=10, seconds=10),
            ),
        )
    )
    assert merge == expect
