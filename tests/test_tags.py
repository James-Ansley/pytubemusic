from pprint import pformat

from approvaltests import verify
from pydantic import ValidationError
from pytest import raises

from pytubemusic.model.user.tags import AlbumTags, Tags, TrackTags
from tests import test


@test()
def track_tags_can_be_created_with_minimal_data():
    data = {"title": "My Track Title"}
    tags = TrackTags(**data)
    assert isinstance(tags, TrackTags)
    assert tags.as_dict() == data


@test(depends_on=("track_tags_can_be_created_with_minimal_data",))
def track_tags_must_be_created_with_a_title():
    raises(ValidationError, lambda: TrackTags(**{}))
    raises(ValidationError, lambda: TrackTags(**{"genre": "Modern"}))
    raises(ValidationError, lambda: TrackTags(**{"album": "My Album Title"}))


@test()
def album_tags_can_be_created_with_minimal_data():
    data = {"album": "My Album Title"}
    tags = AlbumTags(**data)
    assert isinstance(tags, AlbumTags)
    assert tags.as_dict() == data


@test(depends_on=("album_tags_can_be_created_with_minimal_data",))
def album_tags_must_be_created_with_an_album():
    raises(ValidationError, lambda: AlbumTags(**{}))
    raises(ValidationError, lambda: AlbumTags(**{"genre": "Modern"}))
    raises(ValidationError, lambda: AlbumTags(**{"title": "My Track Title"}))


@test(
    depends_on=(
          "track_tags_can_be_created_with_minimal_data",
          "album_tags_can_be_created_with_minimal_data",
    )
)
def tags_can_be_merged():
    tags1 = TrackTags(**{"title": "My Track Title"})
    tags2 = AlbumTags(**{"album": "My Album Title"})
    tags = tags1 + tags2
    assert isinstance(tags, Tags)
    assert tags.as_dict() == {
        "title": "My Track Title",
        "album": "My Album Title",
    }


@test(depends_on=("tags_can_be_merged",))
def leftmost_tags_take_precedence_when_merging():
    tags1 = TrackTags(**{"title": "My Track Title", "genre": "Modern"})
    tags2 = AlbumTags(**{"album": "My Album Title", "genre": "Jazz"})
    tags3 = Tags(**{"title": "FooBar", "genre": "Classical"})
    tags = tags1 + tags2 + tags3
    assert isinstance(tags, Tags)
    assert tags.as_dict() == {
        "title": "My Track Title",
        "album": "My Album Title",
        "genre": "Modern",
    }


@test(
    depends_on=(
          "track_tags_can_be_created_with_minimal_data",
          "album_tags_can_be_created_with_minimal_data",
    )
)
def tags_are_pretty_printed():
    tags1 = TrackTags(**{"title": "My Track Title", "genre": "Modern"})
    tags2 = AlbumTags(**{"album": "My Album Title", "genre": "Jazz"})
    tags3 = Tags(**{"title": "FooBar", "genre": "Classical"})
    tag_fmt = "\n\n".join(pformat(tag) for tag in (tags1, tags2, tags3))
    verify(tag_fmt)
