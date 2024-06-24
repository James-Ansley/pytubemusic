from datetime import timedelta
from pprint import pformat

from approvaltests import verify
from pydantic import ValidationError
from pytest import raises

from pytubemusic.model.user import File, TrackTags, Url
from pytubemusic.model.user.track import (Merge, Playlist,
                                          Single, Split, Track)
from tests import test
from tests.utils import load_toml


@test()
def tracks_cannot_be_created_from_empty_data():
    raises(ValidationError, lambda: Track(**{}))


@test(
    depends_on=("test_tags.py::track_tags_can_be_created_with_minimal_data",),
    scope="session",
)
def singles_can_be_created_with_minimal_data():
    data = load_toml("single_minimal.toml")
    track = Track(**data)
    assert isinstance(track, Single)
    verify(pformat(track))


@test(depends_on=("singles_can_be_created_with_minimal_data",))
def single_urls_must_have_a_watch_id():
    data = {"url": "www.example.com", "metadata": {"title": "My Track Title"}}
    raises(ValidationError, lambda: Single(**data))


@test(depends_on=("singles_can_be_created_with_minimal_data",))
def single_metadata_must_include_track_tag_data():
    data = {
        "url": "www.example.com/watch?v=",
        "metadata": {"album": "My Album Title"}
    }
    raises(ValidationError, lambda: Single(**data))


@test(depends_on=("singles_can_be_created_with_minimal_data",))
def singles_must_not_contain_extra_fields():
    data = {
        "url": "www.example.com/watch?v=",
        "metadata": {"title": "My Track Title"},
        "foo": "bar",
    }
    raises(ValidationError, lambda: Single(**data))


@test(depends_on=("singles_can_be_created_with_minimal_data",))
def singles_must_have_a_url_and_metadata():
    raises(ValidationError, lambda: Single(**{
        "url": "www.example.com/watch?v=",
    }))
    raises(ValidationError, lambda: Single(**{
        "metadata": {"title": "My Track Title"},
    }))


@test(
    depends_on=(
          "test_track.py::singles_can_be_created_with_minimal_data",
          "test_cover.py::url_covers_can_be_created_with_a_hyperlink",
          "test_cover.py::file_covers_can_be_created_with_a_path",
    ),
    scope="session",
)
def singles_can_have_file_or_url_covers():
    data = {
        "url": "www.example.com/watch?v=",
        "metadata": {"title": "My Track Title"}
    }
    track = Single(**data | {"cover": {"path": "data/pic.jpeg"}})
    assert track.cover == File(**{"path": "data/pic.jpeg"})
    track = Single(**data | {"cover": {"href": "www.example.com/pic.jpeg"}})
    assert track.cover == Url(**{"href": "www.example.com/pic.jpeg"})


@test(depends_on=("singles_can_be_created_with_minimal_data",))
def singles_can_be_created_with_start_and_end_times():
    data = {
        "url": "www.example.com/watch?v=",
        "metadata": {"title": "My Track Title"}
    }
    track1 = Single(**data | {"start": "00:00:01.5"})
    track2 = Single(**data | {"end": "00:03:21"})
    track3 = Single(**data | {"start": "00:00:01.5", "end": "00:03:21.0"})
    assert track1.start == timedelta(seconds=1, milliseconds=500)
    assert track2.end == timedelta(minutes=3, seconds=21)
    assert track3.start == timedelta(seconds=1, milliseconds=500)
    assert track3.end == timedelta(minutes=3, seconds=21)


@test(
    depends_on=(
          "test_track.py::singles_can_be_created_with_minimal_data",
          "test_cover.py::url_covers_can_be_created_with_a_hyperlink",
          "test_cover.py::file_covers_can_be_created_with_a_path",
    ),
    scope="session",
)
def singles_can_be_created_with_full_data():
    data = load_toml("single_full.toml")
    single = Single(**data)
    verify(pformat(single))


@test(
    depends_on=("test_tags.py::track_tags_can_be_created_with_minimal_data",),
    scope="session",
)
def split_tracks_can_be_created_with_minimal_data():
    data = load_toml("split_track_minimal.toml")
    split = Track(**data)
    assert isinstance(split, Split)
    verify(pformat(split))


@test(depends_on=("split_tracks_can_be_created_with_minimal_data",))
def split_tracks_cannot_be_created_with_empty_track_lists():
    raises(
        ValidationError,
        lambda: Split(**{"url": "www.example.com/watch?v=", "tracks": []}),
    )


@test(depends_on=("split_tracks_can_be_created_with_minimal_data",))
def split_track_urls_must_have_a_watch_id():
    data = {
        "url": "www.example.com",
        "tracks": [{"metadata": {"title": "My Track Title"}}],
    }
    raises(ValidationError, lambda: Split(**data))


@test(depends_on=("split_tracks_can_be_created_with_minimal_data",))
def split_tracks_must_not_contain_extra_fields():
    data = {
        "url": "www.example.com/watch?v=",
        "tracks": [{"metadata": {"title": "My Track Title"}}],
        "foo": "bar",
    }
    raises(ValidationError, lambda: Split(**data))


@test(
    depends_on=(
          "test_track.py::split_tracks_can_be_created_with_minimal_data",
          "test_cover.py::url_covers_can_be_created_with_a_hyperlink",
          "test_cover.py::file_covers_can_be_created_with_a_path",
    ),
    scope="session",
)
def split_tracks_can_be_created_with_full_data():
    data = load_toml("split_track_full.toml")
    single = Split(**data)
    verify(pformat(single))


@test()
def playlists_can_be_created_with_minimal_data():
    data = load_toml("playlist_minimal.toml")
    playlist = Track(**data)
    assert isinstance(playlist, Playlist)
    assert playlist.url == data["url"]
    assert playlist.cover is None
    assert playlist.tracks == ()


@test(depends_on=("playlists_can_be_created_with_minimal_data",))
def playlists_must_have_a_valid_id():
    data = {"url": "www.example.com"}
    raises(ValidationError, lambda: Playlist(**data))


@test(depends_on=("playlists_can_be_created_with_minimal_data",))
def playlists_must_not_contain_extra_fields():
    data = {
        "url": "www.example.com/playlist?list=",
        "foo": "bar",
    }
    raises(ValidationError, lambda: Playlist(**data))


@test(
    depends_on=(
          "test_track.py::playlists_can_be_created_with_minimal_data",
          "test_tags.py::track_tags_can_be_created_with_minimal_data",
    ),
    scope="session",
)
def playlist_tracks_can_be_dropped():
    data = {
        "url": "www.example.com/playlist?list=",
        "tracks": [
            {"metadata": {"title": "My Track Title"}},
            {"drop": True},
            {"metadata": {"title": "My Other Track Title"}},
        ]
    }
    playlist = Playlist(**data)
    verify(pformat(playlist))


@test(
    depends_on=(
          "test_track.py::playlists_can_be_created_with_minimal_data",
          "test_tags.py::track_tags_can_be_created_with_minimal_data",
          "test_cover.py::url_covers_can_be_created_with_a_hyperlink",
          "test_cover.py::file_covers_can_be_created_with_a_path",
    ),
    scope="session",
)
def playlist_tracks_can_be_merged():
    data = load_toml("playlist_with_merge.toml")
    playlist = Playlist(**data)
    verify(pformat(playlist))


@test(
    depends_on=(
          "test_track.py::playlists_can_be_created_with_minimal_data",
          "test_tags.py::track_tags_can_be_created_with_minimal_data",
          "test_cover.py::url_covers_can_be_created_with_a_hyperlink",
          "test_cover.py::file_covers_can_be_created_with_a_path",
    ),
    scope="session",
)
def playlists_can_be_created_with_full_data():
    data = load_toml("playlist_full.toml")
    playlist = Track(**data)
    verify(pformat(playlist))


@test(
    depends_on=("test_tags.py::track_tags_can_be_created_with_minimal_data",),
    scope="session",
)
def merge_tracks_can_be_created_with_minimal_data():
    data = load_toml("merge_minimal.toml")
    merge = Track(**data)
    assert isinstance(merge, Merge)
    assert merge.metadata == TrackTags(**data["metadata"])
    assert len(merge.parts) == 1
    assert merge.parts[0].url == "www.example.com/watch?v="


@test(depends_on=("merge_tracks_can_be_created_with_minimal_data",))
def merge_tracks_must_contain_at_least_one_track():
    data = {"metadata": {"title": "My Track Title"}, "parts": []}
    raises(ValidationError, lambda: Merge(**data))


@test(depends_on=("merge_tracks_can_be_created_with_minimal_data",))
def merge_track_urls_must_contain_a_valid_id():
    data = {
        "metadata": {"title": "My Track Title"},
        "parts": [{"url": "www.example.com"}]
    }
    raises(ValidationError, lambda: Merge(**data))


@test(depends_on=("merge_tracks_can_be_created_with_minimal_data",))
def merge_tracks_cannot_contain_extra_fields():
    data = {
        "metadata": {"title": "My Track Title"},
        "parts": [{"url": "www.example.com/watch?v="}],
        "foo": "bar"
    }
    raises(ValidationError, lambda: Merge(**data))


@test(
    depends_on=(
          "test_track.py::merge_tracks_can_be_created_with_minimal_data",
          "test_cover.py::url_covers_can_be_created_with_a_hyperlink",
          "test_cover.py::file_covers_can_be_created_with_a_path",
    ),
    scope="session",
)
def merge_tracks_can_be_created_with_full_data():
    data = load_toml("merge_full.toml")
    merge = Track(**data)
    verify(pformat(merge))
