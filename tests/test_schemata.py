import tomllib

import pytest
from jsonschema.exceptions import ValidationError

from pytubemusic.validation import validate


def test_minimal_track_part():
    data = {
        "type": "track",
        "url": "https://www.youtube.com/watch?v=00000000000",
        "metadata": {"title": "Track1"}
    }
    validate(data, "components/track")


def test_track_part():
    data = {
        "type": "track",
        "url": "https://www.youtube.com/watch?v=00000000000",
        "start": "00:01",
        "end": "1:00:05",
        "metadata": {"title": "Track1"}
    }
    validate(data, "components/track")


def test_minimal_split_part():
    data = {
        "type": "split",
        "url": "https://www.youtube.com/watch?v=00000000000",
        "tracks": [
            {"metadata": {"title": "Track1"}},
        ]
    }
    validate(data, "components/split")


def test_split_part():
    validate(
        {
            "type": "split",
            "url": "https://www.youtube.com/watch?v=00000000000",
            "tracks": [
                {"start": "00:01", "metadata": {"title": "Track1"}},
                {"end": "5:00", "metadata": {"title": "Track2"}},
                {"start": "00:01", "end": "12:34",
                 "metadata": {"title": "Track3"}},
            ]
        },
        "components/split",
    )
    with pytest.raises(ValidationError):
        # Missing metadata
        validate(
            {
                "type": "split",
                "url": "https://www.youtube.com/watch?v=00000000000",
                "tracks": [
                    {"start": "00:01", "metadata": {"title": "Track1"}},
                    {"end": "5:00", "metadata": {"title": "Track2"}},
                    {"start": "00:01", "end": "12:34"},
                ]
            },
            "components/split",
        )


def test_minimal_playlist_part():
    validate({
        "type": "playlist",
        "url": "https://www.youtube.com/playlist?"
               "list=0000000000000000000000000000000000",
    }, "components/playlist")
    validate(
        {
            "type": "playlist",
            "join": True,
            "url": "https://www.youtube.com/playlist?"
                   "list=0000000000000000000000000000000000",
            "metadata": {"title": "Track"}
        },
        "components/playlist",
    )

    with pytest.raises(ValidationError):
        # Missing metadata
        validate(
            {
                "type": "playlist",
                "join": True,
                "url": "https://www.youtube.com/playlist?"
                       "list=0000000000000000000000000000000000",
            },
            "components/playlist",
        )

    with pytest.raises(ValidationError):
        # Disallowed Metadata
        validate(
            {
                "type": "playlist",
                "join": False,
                "url": "https://www.youtube.com/playlist?"
                       "list=0000000000000000000000000000000000",
                "metadata": {"title": "Track"}
            },
            "components/playlist",
        )


def test_playlist_part():
    validate(
        {
            "type": "playlist",
            "url": "https://www.youtube.com/playlist?"
                   "list=0000000000000000000000000000000000",
            "tracks": [
                {"start": "00:01", "metadata": {"title": "Track1"}},
                {"end": "5:00", "metadata": {"title": "Track2"}},
                {"start": "00:01", "end": "12:34",
                 "metadata": {"title": "Track3"}},
            ]
        },
        "components/playlist"
    )
    validate(
        {
            "type": "playlist",
            "join": True,
            "url": "https://www.youtube.com/playlist?"
                   "list=0000000000000000000000000000000000",
            "tracks": [
                {"start": "00:01"},
                {"end": "5:00"},
                {"start": "00:01", "end": "12:34"},
            ],
            "metadata": {"title": "Track"}
        },
        "components/playlist"
    )
    with pytest.raises(ValidationError):
        # Missing metadata
        validate(
            {
                "type": "playlist",
                "url": "https://www.youtube.com/playlist?"
                       "list=0000000000000000000000000000000000",
                "tracks": [
                    {"start": "00:01", "metadata": {"title": "Track1"}},
                    {"end": "5:00", "metadata": {"title": "Track2"}},
                    {"start": "00:01", "end": "12:34"},
                ]
            },
            "components/playlist",
        )

    with pytest.raises(ValidationError):
        # Disallowed Metadata
        validate(
            {
                "type": "playlist",
                "join": False,
                "url": "https://www.youtube.com/playlist?"
                       "list=0000000000000000000000000000000000",
                "tracks": [
                    {"start": "00:01", "metadata": {"title": "Track1"}},
                    {"end": "5:00", "metadata": {"title": "Track2"}},
                    {"start": "00:01", "end": "12:34",
                     "metadata": {"title": "Track3"}},
                ],
                "metadata": {"title": "Track"},
            },
            "components/playlist",
        )


def test_minimal_merge_part():
    validate(
        {
            "type": "merge",
            "tracks": [
                {"url": "https://www.youtube.com/watch?v=00000000000"},
            ],
            "metadata": {"title": "Track"},
        },
        "components/merge",
    )
    with pytest.raises(ValidationError):
        # empty tracks
        validate(
            {"type": "merge", "tracks": [], "metadata": {"title": "Track"}},
            "components/merge",
        )
    with pytest.raises(ValidationError):
        # missing metadata
        validate(
            {
                "type": "merge",
                "tracks": [
                    {"url": "https://www.youtube.com/watch?v=00000000000"},
                ],
            },
            "components/merge",
        )
    with pytest.raises(ValidationError):
        # missing url
        validate(
            {"type": "merge", "tracks": [{"start": "00:00"}]},
            "components/merge",
        )


def test_merge_part():
    validate(
        {
            "type": "merge",
            "tracks": [
                {"start": "00:01",
                 "url": "https://www.youtube.com/watch?v=00000000000"},
                {"end": "5:00",
                 "url": "https://www.youtube.com/watch?v=00000000001"},
                {"start": "00:01", "end": "12:34",
                 "url": "https://www.youtube.com/watch?v=00000000002"},
            ],
            "metadata": {"title": "Track"},
        },
        "components/merge",
    )


def test_album_metadata():
    validate({"album": "AnAlbum"}, "components/album_metadata")
    with pytest.raises(ValidationError):
        validate({"title": "AnAlbum"}, "components/album_metadata")


def test_track_metadata():
    validate({"title": "ATrack"}, "components/track_metadata")
    with pytest.raises(ValidationError):
        validate({"album": "ATrack"}, "components/track_metadata")


def test_start_timestamp():
    validate("00:00", "components/start_timestamp")
    validate("0:00.00", "components/start_timestamp")
    validate("00:00:00", "components/start_timestamp")
    validate("0:00:00.00", "components/start_timestamp")
    validate("00:00:00.00", "components/start_timestamp")

    with pytest.raises(ValidationError):
        validate("123", "components/start_timestamp")


def test_end_timestamp():
    validate("00:00", "components/end_timestamp")
    validate("0:00.00", "components/end_timestamp")
    validate("00:00:00", "components/end_timestamp")
    validate("0:00:00.00", "components/end_timestamp")
    validate("00:00:00.00", "components/end_timestamp")

    with pytest.raises(ValidationError):
        validate("123", "components/start_timestamp")


def test_cover():
    validate({"url": "www.google.com/img.jpg"}, "components/cover")
    validate({"file": "img.jpg"}, "components/cover")


@pytest.mark.parametrize(
    "path",
    (
            "data/schemata/minimal_album_split.toml",
            "data/schemata/minimal_album_merge.toml",
            "data/schemata/minimal_album_track.toml",
            "data/schemata/minimal_album_playlist.toml",
            "data/schemata/album.toml",
    )
)
@pytest.mark.parametrize("type_", ("album", "type"))
def test_minimal_album(path, type_):
    with open(path, "rb") as f:
        validate(tomllib.load(f), type_)


@pytest.mark.parametrize(
    "path",
    (
            "data/schemata/album_missing_metadata.toml",
    )
)
@pytest.mark.parametrize("type_", ("album", "type"))
def test_error_album(path, type_):
    with pytest.raises(ValidationError):
        with open(path, "rb") as f:
            validate(tomllib.load(f), type_)
