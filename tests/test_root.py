from pprint import pformat

from approvaltests import verify

from pytubemusic.model.user import Merge, Playlist, Single, Split
from pytubemusic.model.user.album import Album
from pytubemusic.model.user.root import Media
from tests import test
from tests.utils import load_toml


@test(
    depends_on=(
          "test_track.py::singles_can_be_created_with_full_data",
    ),
    scope="session"
)
def root_user_model_can_parse_a_single():
    data = load_toml("single_full.toml")
    media = Media(**data)
    assert isinstance(media, Single)
    verify(pformat(media))


@test(
    depends_on=(
          "test_track.py::split_tracks_can_be_created_with_full_data",
    ),
    scope="session"
)
def root_user_model_can_parse_a_split_track():
    data = load_toml("split_track_full.toml")
    media = Media(**data)
    assert isinstance(media, Split)
    verify(pformat(media))


@test(
    depends_on=(
          "test_track.py::playlists_can_be_created_with_full_data",
    ),
    scope="session"
)
def root_user_model_can_parse_a_playlist():
    data = load_toml("playlist_full.toml")
    media = Media(**data)
    assert isinstance(media, Playlist)
    verify(pformat(media))


@test(
    depends_on=(
          "test_track.py::merge_tracks_can_be_created_with_full_data",
    ),
    scope="session"
)
def root_user_model_can_parse_a_merge_track():
    data = load_toml("merge_full.toml")
    media = Media(**data)
    assert isinstance(media, Merge)
    verify(pformat(media))


@test(
    depends_on=(
          "test_track.py::singles_can_be_created_with_full_data",
          "test_track.py::split_tracks_can_be_created_with_full_data",
          "test_track.py::playlists_can_be_created_with_full_data",
          "test_track.py::merge_tracks_can_be_created_with_full_data",
          "test_tags.py::album_tags_can_be_created_with_minimal_data",
    ),
    scope="session"
)
def root_user_model_can_parse_album():
    data = load_toml("album_full.toml")
    media = Media(**data)
    assert isinstance(media, Album)
    verify(pformat(media))
