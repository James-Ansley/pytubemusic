from pathlib import Path

from pytubemusic.model.cover import *
from utils import test


@test
def a_url_cover_will_convert_to_a_uri():
    cover1 = Url(href="www.example.com")
    cover2 = Url(href="http://www.example.com")
    assert cover1.as_uri() == "https://www.example.com"
    assert cover2.as_uri() == "http://www.example.com"


@test
def a_file_cover_will_convert_to_a_uri():
    file1 = File(path=Path("/foo.txt"))
    file2 = File(path=Path("/bar/foo.txt"))
    assert file1.as_uri() == "file:///foo.txt"
    assert file2.as_uri() == "file:///bar/foo.txt"
