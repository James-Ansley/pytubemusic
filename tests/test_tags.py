from pytubemusic.model import *
from .utils import test


@test
def two_tags_can_merge_attributes():
    track_tags = TrackTags(title="My Track Title")
    album_tags = AlbumTags(album="My Album Name")
    expected = Tags(title="My Track Title", album="My Album Name")
    assert track_tags + album_tags == expected


@test
def tag_attributes_on_the_lhs_of_merges_take_precedence():
    track_tags = TrackTags(title="My Track Title")
    album_tags = AlbumTags(album="My Album Name", title="My overridden title")
    expected = Tags(title="My Track Title", album="My Album Name")
    assert track_tags + album_tags == expected


@test
def several_tags_can_merge_into_one():
    tags1 = TrackTags(title="Title")
    tags2 = TrackTags(title="Overridden Title", composer="Composer")
    tags3 = AlbumTags(album="Album", composer="Overridden Composer")
    expected = Tags(title="Title", album="Album", composer="Composer")
    assert tags1 + tags2 + tags3 == expected
