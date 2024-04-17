from datetime import timedelta

from pytubemusic.model import *
from utils import test


@test
def a_single_can_be_flattened_into_track_data():
    single = Single(
        url="www.example.com",
        metadata=TrackTags(title="My Single Title"),
        cover=None,
        start="00:00:01",
        end="00:07:23",
    )
    expect = TrackData(
        metadata=Tags(title="My Single Title"),
        cover=None,
        track_parts=(
            AudioData(
                url="www.example.com",
                start=timedelta(seconds=1),
                end=timedelta(minutes=7, seconds=23),
            ),
        ),
    ),
    assert tuple(TrackData.from_track(single)) == expect


@test
def a_single_can_be_flattened_to_track_data_with_additional_metadata():
    single = Single(
        url="https://www.example.com",
        metadata=TrackTags(title="My Title"),
        cover=Url(href="https://www.example.com/photo.jpg"),
    )
    album_metadata = AlbumTags(album="My Album", composer="Mx Composer")
    expect = TrackData(
        metadata=Tags(
            title="My Title",
            album="My Album",
            composer="Mx Composer",
        ),
        cover="https://www.example.com/photo.jpg",
        track_parts=(AudioData(url="https://www.example.com"),),
    ),
    assert tuple(TrackData.from_track(single, album_metadata)) == expect


@test
def additional_metadata_does_not_override_flattened_single_metadata():
    single = Single(url="my_url", metadata=TrackTags(title="Title", track=1))
    album_metadata = AlbumTags(album="Album", title="Overridden", track=-1)
    expect = TrackData(
        metadata=Tags(title="Title", album="Album", track=1),
        cover=None,
        track_parts=(AudioData(url="my_url"),)
    ),
    assert tuple(TrackData.from_track(single, album_metadata)) == expect


@test
def flattened_singles_can_be_given_a_cover():
    single = Single(url="my_url", metadata=TrackTags(title="Title"))
    cover = Url(href="www.example.com")
    expect = TrackData(
        metadata=Tags(title="Title"),
        cover="https://www.example.com",
        track_parts=(AudioData(url="my_url"),),
    ),
    assert tuple(TrackData.from_track(single, cover=cover)) == expect


@test
def flattened_singles_will_keep_their_covers_even_if_another_is_given():
    single = Single(
        url="my_url",
        metadata=TrackTags(title="Title"),
        cover=File(path="/my_file.jpg"),
    )
    cover = Url(href="www.example.com")
    expect = TrackData(
        metadata=Tags(title="Title"),
        cover="file:///my_file.jpg",
        track_parts=(AudioData(url="my_url"),),
    ),
    assert tuple(TrackData.from_track(single, cover=cover)) == expect


@test
def split_tracks_can_be_flattened_to_multiple_track_data_objects():
    split = Split(
        url="www.example.com",
        tracks=(
            TrackStub(metadata=TrackTags(title="Track 1"), start="00:00:05"),
            TrackStub(metadata=TrackTags(title="Track 2"), start="00:00:10"),
            TrackStub(metadata=TrackTags(title="Track 3"), start="00:00:15"),
        )
    )
    expect = (
        TrackData(
            metadata=Tags(title="Track 1"),
            cover=None,
            track_parts=[
                AudioData(
                    url="www.example.com",
                    start=timedelta(seconds=5),
                    end=timedelta(seconds=10),
                )
            ],
        ),
        TrackData(
            metadata=Tags(title="Track 2"),
            cover=None,
            track_parts=[
                AudioData(
                    url="www.example.com",
                    start=timedelta(seconds=10),
                    end=timedelta(seconds=15),
                ),
            ],
        ),
        TrackData(
            metadata=Tags(title="Track 3"),
            cover=None,
            track_parts=[
                AudioData(
                    url="www.example.com",
                    start=timedelta(seconds=15),
                    end=None
                )
            ],
        ),
    )
    assert tuple(TrackData.from_track(split)) == expect


@test
def a_split_track_containing_a_single_track_can_be_flattened():
    split = Split(
        url="www.example.com",
        tracks=(
            TrackStub(metadata=TrackTags(title="Track 1"), start="00:00:05"),
        )
    )
    expect = (
        TrackData(
            metadata=Tags(title="Track 1"),
            cover=None,
            track_parts=[
                AudioData(url="www.example.com", start=timedelta(seconds=5)),
            ],
        ),
    )
    assert tuple(TrackData.from_track(split)) == expect


@test
def a_playlist_can_be_flattened_into_track_data():
    playlist = Playlist(
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
    expect = (
        TrackData(
            metadata=Tags(title="My Title 1"),
            cover="https://www.example.com/pic.jpeg",
            track_parts=(PlaylistAudioData(
                url="www.example.com",
                index=0,
                start=timedelta(seconds=1),
                end=timedelta(minutes=1, seconds=23),
            ),)
        ),
        TrackData(
            metadata=Tags(title="My Title 3"),
            cover="https://www.example.com/pic.jpeg",
            track_parts=(PlaylistAudioData(
                url="www.example.com",
                index=2,
                start=timedelta(minutes=5, seconds=56),
                end=timedelta(minutes=10, seconds=10),
            ),)
        ),
    )
    assert tuple(TrackData.from_track(playlist)) == expect


@test
def a_merge_playlist_can_be_flattened_into_track_data():
    playlist = MergePlaylist(
        url="www.example.com",
        cover=Url(href="www.example.com/pic.jpeg"),
        metadata=TrackTags(title="My Title 1"),
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
    expect = (
        TrackData(
            metadata=Tags(title="My Title 1"),
            cover="https://www.example.com/pic.jpeg",
            track_parts=(
                PlaylistAudioData(
                    url="www.example.com",
                    index=0,
                    start=timedelta(seconds=1),
                    end=timedelta(minutes=1, seconds=23),
                ),
                PlaylistAudioData(
                    url="www.example.com",
                    index=2,
                    start=timedelta(minutes=5, seconds=56),
                    end=timedelta(minutes=10, seconds=10),
                ),
            )
        ),
    )
    assert tuple(TrackData.from_track(playlist)) == expect


@test
def a_merge_can_be_flattened_into_track_data():
    playlist = Merge(
        metadata=TrackTags(title="My Title 1"),
        cover=Url(href="www.example.com/pic.jpeg"),
        tracks=(
            AudioStub(
                url="www.example.com/1",
                start=timedelta(seconds=1),
                end=timedelta(minutes=1, seconds=23),
            ),
            AudioStub(
                url="www.example.com/2",
                start=timedelta(minutes=5, seconds=56),
                end=timedelta(minutes=10, seconds=10),
            ),
        )
    )
    expect = (
        TrackData(
            metadata=Tags(title="My Title 1"),
            cover="https://www.example.com/pic.jpeg",
            track_parts=(
                AudioData(
                    url="www.example.com/1",
                    start=timedelta(seconds=1),
                    end=timedelta(minutes=1, seconds=23),
                ),
                AudioData(
                    url="www.example.com/2",
                    start=timedelta(minutes=5, seconds=56),
                    end=timedelta(minutes=10, seconds=10),
                ),
            )
        ),
    )
    assert tuple(TrackData.from_track(playlist)) == expect