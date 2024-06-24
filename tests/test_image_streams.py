from pathlib import Path

from pytubemusic.model.user import File, Url
from pytubemusic.streams.images import as_uri
from tests import test


@test()
def none_cover_images_are_ignored_when_turned_to_uris():
    assert as_uri(None) is None


# noinspection HttpUrlsUsage
@test(
    depends_on=("test_cover.py::url_covers_can_be_created_with_a_hyperlink",),
    scope="session",
)
def url_covers_can_be_converted_to_uris():
    cover1 = Url(**{"href": "www.example.com/pic1.jpeg"})
    cover2 = Url(**{"href": "https://www.example.com/pic1.jpeg"})
    cover3 = Url(**{"href": "http://www.example.com/pic1.jpeg"})
    assert as_uri(cover1) == "https://www.example.com/pic1.jpeg"
    assert as_uri(cover2) == "https://www.example.com/pic1.jpeg"
    assert as_uri(cover3) == "http://www.example.com/pic1.jpeg"


@test(
    depends_on=("test_cover.py::file_covers_can_be_created_with_a_path",),
    scope="session",
)
def file_covers_can_be_converted_to_uris():
    cwd = Path.cwd()
    foo = Path("/foo")

    cover1 = File(**{"path": "data/pic1.jpeg"})
    cover2 = File(**{"path": "/Users/user/foo/bar.png"})
    cover3 = File(**{"path": "../data/pic1.jpeg"})
    assert as_uri(cover1) == cwd.joinpath("data/pic1.jpeg").as_uri()
    assert as_uri(cover1, foo) == Path("/foo", "data/pic1.jpeg").as_uri()
    assert as_uri(cover2) == Path("/Users/user/foo/bar.png").as_uri()
    assert as_uri(cover2, foo) == Path("/Users/user/foo/bar.png").as_uri()
    assert as_uri(cover3) == cwd.parent.joinpath("data/pic1.jpeg").as_uri()
    assert as_uri(cover3, foo) == Path("/data/pic1.jpeg").as_uri()
