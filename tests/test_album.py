from pprint import pformat

from approvaltests import verify
from pydantic import ValidationError
from pytest import raises

from pytubemusic.model.user.album import Album
from tests import test
from tests.utils import load_toml


@test(
    depends_on=(
          "test_track.py::singles_can_be_created_with_full_data",
          "test_tags.py::album_tags_can_be_created_with_minimal_data",
    ),
    scope="session"
)
def an_album_can_be_created_with_a_single():
    data = load_toml("album_minimal.toml")
    album = Album(**data)
    assert isinstance(album, Album)
    verify(pformat(album))


@test(
    depends_on=("test_tags.py::album_tags_can_be_created_with_minimal_data",),
    scope="session",
)
def an_album_must_have_at_least_one_track():
    data = {"metadata": {"album": "My Album Title"}, "tracks": []}
    raises(ValidationError, lambda: Album(**data))


@test(
    depends_on=(
          "test_track.py::singles_can_be_created_with_full_data",
          "test_track.py::split_tracks_can_be_created_with_full_data",
          "test_track.py::playlists_can_be_created_with_full_data",
          "test_track.py::merge_tracks_can_be_created_with_full_data",
          "test_cover.py::url_covers_can_be_created_with_a_hyperlink",
          "test_cover.py::file_covers_can_be_created_with_a_path",
          "test_tags.py::album_tags_can_be_created_with_minimal_data",
    ),
    scope="session",
)
def an_album_can_be_created_with_all_track_types():
    data = load_toml("album_full.toml")
    album = Album(**data)
    assert isinstance(album, Album)
    verify(pformat(album))
