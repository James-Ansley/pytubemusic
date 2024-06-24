from pathlib import Path
from pprint import pformat

from approvaltests import verify

from pytubemusic.model.user.cover import File, Url
from tests import test


@test()
def url_covers_can_be_created_with_a_hyperlink():
    data = {"href": "www.example.com/pic1.jpeg"}
    cover = Url(**data)
    assert isinstance(cover, Url)
    assert cover.href == data["href"]


@test()
def file_covers_can_be_created_with_a_path():
    data = {"path": "data/pic1.jpeg"}
    cover = File(**data)
    assert isinstance(cover, File)
    assert cover.path == Path("data/pic1.jpeg")


@test(
    depends_on=(
          "url_covers_can_be_created_with_a_hyperlink",
          "file_covers_can_be_created_with_a_path",
    )
)
def covers_can_be_pretty_printed():
    cover1 = Url(**{"href": "www.example.com/pic1.jpeg"})
    cover2 = File(**{"path": "data/pic1.jpeg"})
    cover_fmt = "\n\n".join(pformat(tag) for tag in (cover1, cover2))
    verify(cover_fmt)
