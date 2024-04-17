from datetime import timedelta

from pydantic import ValidationError
from pytest import raises

from pytubemusic.model import *
from utils import test


@test
def an_album_cannot_be_created_with_zero_tracks():
    with raises(ValidationError):
        Album(metadata=AlbumTags(album="My Album"))


@test
def an_album_can_be_created_from_minimal_data():
    album = Album(**{
        "metadata": {"album": "My Album"},
        "tracks": (
            {"url": "www.example.com", "metadata": {"title": "My Track"}},
        )
    })
    expect = Album(
        metadata=AlbumTags(album="My Album"),
        tracks=(
            Single(url="www.example.com", metadata=TrackTags(title="My Track")),
        )
    )
    assert album == expect


@test
def an_album_can_be_created_from_full_data():
    album = Album(**{
        "metadata": {"album": "My Album"},
        "cover": {"path": "/foo.jpeg"},
        "tracks": (
            {"url": "www.example.com", "metadata": {"title": "My Track"}},
            {
                "url": "www.example.com",
                "tracks": ({"metadata": {"title": "My Track 2"}},),
            },
            {
                "url": "www.example.com",
                "metadata": {"title": "My Track 2.5"},
                "tracks": ({"start": "00:00:01"},),
            },
            {
                "metadata": {"title": "My Track 3"},
                "tracks": ({"url": "www.example.com"},)
            },
        )
    })
    expect = Album(
        metadata=AlbumTags(album="My Album"),
        cover=File(path="/foo.jpeg"),
        tracks=(
            Single(url="www.example.com", metadata=TrackTags(title="My Track")),
            Split(
                url="www.example.com",
                tracks=(TrackStub(metadata=TrackTags(title="My Track 2")),),
            ),
            MergePlaylist(
                url="www.example.com",
                metadata=TrackTags(title="My Track 2.5"),
                tracks=(TimeStub(start=timedelta(seconds=1)),)
            ),
            Merge(
                metadata=TrackTags(title="My Track 3"),
                tracks=(AudioStub(url="www.example.com"),)
            )
        )
    )
    assert album == expect
