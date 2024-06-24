from datetime import timedelta
from pprint import pformat

from pytest import approx
from approvaltests import verify

from pytubemusic.model.track.track_data import (
    TrackData,
    AudioData,
    PlaylistAudioData,
)
from pytubemusic.model.user import (
    Album,
    File,
    Media,
    Merge,
    Playlist,
    Single,
    Split,
    Tags,
    Url,
)
from tests import test
from tests.utils import load_toml


@test()
def audio_data_can_list_start_seconds_and_duration_seconds():
    audio = AudioData(
        url="www.example.com/watch?v=",
        start=timedelta(seconds=1, milliseconds=500),
        end=timedelta(seconds=2, milliseconds=600),
    )
    assert audio.start_second() == approx(1.5)
    assert audio.duration_seconds() == approx(1.1)
    audio = AudioData(
        url="www.example.com/watch?v=",
        start=None,
        end=timedelta(seconds=2, milliseconds=600),
    )
    assert audio.start_second() is None
    assert audio.duration_seconds() == approx(2.6)
    audio = AudioData(
        url="www.example.com/watch?v=",
        start=timedelta(seconds=1, milliseconds=500),
        end=None
    )
    assert audio.start_second() == approx(1.5)
    assert audio.duration_seconds() is None
    audio = AudioData(
        url="www.example.com/watch?v=",
        start=None,
        end=None
    )
    assert audio.start_second() is None
    assert audio.duration_seconds() is None


@test()
def playlist_audio_data_can_list_start_seconds_and_duration_seconds():
    audio = PlaylistAudioData(
        url="www.example.com/watch?v=",
        index=0,
        start=timedelta(seconds=1, milliseconds=500),
        end=timedelta(seconds=2, milliseconds=600),
    )
    assert audio.start_second() == approx(1.5)
    assert audio.duration_seconds() == approx(1.1)
    audio = PlaylistAudioData(
        url="www.example.com/watch?v=",
        index=0,
        start=None,
        end=timedelta(seconds=2, milliseconds=600),
    )
    assert audio.start_second() is None
    assert audio.duration_seconds() == approx(2.6)
    audio = PlaylistAudioData(
        url="www.example.com/watch?v=",
        index=0,
        start=timedelta(seconds=1, milliseconds=500),
        end=None
    )
    assert audio.start_second() == approx(1.5)
    assert audio.duration_seconds() is None
    audio = PlaylistAudioData(
        url="www.example.com/watch?v=",
        index=0,
        start=None,
        end=None
    )
    assert audio.start_second() is None
    assert audio.duration_seconds() is None


@test(
    depends_on=(
          "test_track.py::singles_can_be_created_with_minimal_data",
          "test_track.py::singles_can_be_created_with_full_data",
    ),
    scope="session",
)
def singles_can_be_converted_to_track_data():
    single = Single(**load_toml("single_full.toml"))
    track_data = next(TrackData.from_single(single))
    audio = AudioData(
        url="www.example.com/watch?v=",
        start=timedelta(seconds=1, milliseconds=500),
        end=timedelta(minutes=3, seconds=21),
    )
    assert track_data.metadata == Tags(title="My Track Title")
    assert track_data.cover == File(path="data/pic.jpeg")
    assert tuple(track_data.parts) == (audio,)

    single = Single(**load_toml("single_minimal.toml"))
    track_data, = TrackData.from_single(single)
    audio = AudioData(url="www.example.com/watch?v=")
    assert track_data.metadata == Tags(title="My Track Title")
    assert track_data.cover is None
    assert tuple(track_data.parts) == (audio,)


@test(
    depends_on=(
          "test_track.py::split_tracks_can_be_created_with_minimal_data",
          "test_track.py::split_tracks_can_be_created_with_full_data",
    ),
    scope="session",
)
def split_tracks_can_be_converted_to_track_data():
    split = Split(**load_toml("split_track_full.toml"))
    track1, track2 = TrackData.from_split(split)
    audio = AudioData(
        url="www.example.com/watch?v=",
        start=timedelta(seconds=1, milliseconds=500),
        end=timedelta(seconds=12, milliseconds=300),
    )
    assert track1.metadata == Tags(title="My First Track Title")
    assert track1.cover == Url(href="www.example.com/pic2.jpeg")
    assert tuple(track1.parts) == (audio,)
    audio = AudioData(
        url="www.example.com/watch?v=",
        start=timedelta(seconds=12, milliseconds=300),
        end=timedelta(minutes=43, seconds=21),
    )
    assert track2.metadata == Tags(title="My Second Track Title")
    assert track2.cover == Url(href="www.example.com/pic1.jpeg")
    assert tuple(track2.parts) == (audio,)

    split = Split(**load_toml("split_track_minimal.toml"))
    track, = TrackData.from_split(split)
    assert track.metadata == Tags(title="My Track Title")
    assert track.cover is None
    assert tuple(track.parts) == (
        AudioData(url="www.example.com/watch?v="),
    )


@test(
    depends_on=(
          "test_track.py::playlists_can_be_created_with_minimal_data",
          "test_track.py::playlists_can_be_created_with_full_data",
          "test_track.py::playlist_tracks_can_be_merged",
    ),
    scope="session",
)
def playlists_can_be_converted_to_track_data():
    playlist = Playlist(**load_toml("playlist_full.toml"))
    track1, track2 = TrackData.from_playlist(playlist)
    assert track1.metadata == Tags(title="My Track Title")
    assert track1.cover == Url(href="www.example.com/pic2.jpeg")
    audio = PlaylistAudioData(
        url="www.example.com/playlist?list=",
        index=0,
        start=timedelta(seconds=1, milliseconds=500),
        end=timedelta(minutes=43, seconds=21),
    )
    assert tuple(track1.parts) == (audio,)

    assert track2.metadata == Tags(title="My Other Track Title")
    assert track2.cover == Url(href="www.example.com/pic1.jpeg")
    audio = PlaylistAudioData(
        url="www.example.com/playlist?list=",
        index=2,
        end=timedelta(minutes=43, seconds=21),
    )
    assert tuple(track2.parts) == (audio,)

    playlist = Playlist(**load_toml("playlist_minimal.toml"))
    assert tuple(TrackData.from_playlist(playlist)) == ()

    playlist = Playlist(**load_toml("playlist_with_merge.toml"))
    track1, track2 = TrackData.from_playlist(playlist)
    assert track1.metadata == Tags(title="My Track Title")
    assert track1.cover == Url(href="www.example.com/pic2.jpeg")
    assert tuple(track1.parts) == (
        PlaylistAudioData(
            url="www.example.com/playlist?list=",
            index=0,
            start=timedelta(seconds=1, milliseconds=500),
            end=timedelta(minutes=43, seconds=21),
        ),
        PlaylistAudioData(
            url="www.example.com/playlist?list=",
            index=2,
            start=timedelta(seconds=1),
            end=None
        ),
        PlaylistAudioData(
            url="www.example.com/playlist?list=",
            index=3,
            start=None,
            end=None
        ),
    )
    assert track2.metadata == Tags(title="My Other Track Title")
    assert track2.cover == Url(href="www.example.com/pic1.jpeg")
    audio = PlaylistAudioData(
        url="www.example.com/playlist?list=",
        index=5,
        end=timedelta(minutes=43, seconds=21),
    )
    assert tuple(track2.parts) == (audio,)


@test(
    depends_on=(
          "test_track.py::merge_tracks_can_be_created_with_minimal_data",
          "test_track.py::merge_tracks_can_be_created_with_full_data",
    ),
    scope="session",
)
def merge_tracks_can_be_converted_to_track_data():
    merge = Merge(**load_toml("merge_full.toml"))
    track, = TrackData.from_merge(merge)
    assert track.metadata == Tags(title="My Track Title")
    assert track.cover == Url(href="www.example.com/pic1.jpeg")
    assert tuple(track.parts) == (
        AudioData(
            url="www.example1.com/watch?v=",
            start=None,
            end=None,
        ),
        AudioData(
            url="www.example2.com/watch?v=",
            start=timedelta(seconds=1, milliseconds=500),
            end=timedelta(minutes=43, seconds=21),
        )
    )


@test(
    depends_on=(
          "singles_can_be_converted_to_track_data",
          "split_tracks_can_be_converted_to_track_data",
          "playlists_can_be_converted_to_track_data",
          "merge_tracks_can_be_converted_to_track_data",
    )
)
def tracks_can_be_converted_to_track_data():
    single = Single(**load_toml("single_full.toml"))
    split = Split(**load_toml("split_track_full.toml"))
    playlist = Playlist(**load_toml("playlist_full.toml"))
    merge = Merge(**load_toml("merge_full.toml"))
    verify(
        "\n\n".join(
            pformat(track)
            for tracks in (single, split, playlist, merge)
            for track in TrackData.from_track(tracks)
        )
    )


@test(depends_on=("tracks_can_be_converted_to_track_data",))
def albums_can_be_converted_to_track_data():
    album = Album(**load_toml("album_full.toml"))
    tracks = tuple(TrackData.from_album(album))
    verify(pformat(tracks))


@test(
    depends_on=(
          "tracks_can_be_converted_to_track_data",
          "albums_can_be_converted_to_track_data",
    )
)
def media_can_be_converted_to_track_data():
    data = (
        load_toml("single_full.toml"),
        load_toml("split_track_full.toml"),
        load_toml("playlist_full.toml"),
        load_toml("merge_full.toml"),
        load_toml("album_full.toml"),
    )
    tracks = (Media(**media) for media in data)
    tracks = (TrackData.from_media(media) for media in tracks)
    tracks = (track for track_group in tracks for track in track_group)
    tracks = tuple(tracks)
    verify(pformat(tracks))
