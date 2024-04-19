from .base import MaybeInt, MaybeStr, Model

__all__ = (
    "Tags",
    "TrackTags",
    "AlbumTags",
    "MaybeTrackTags",
    "MaybeAlbumTags",
    "MaybeTags",
)

type MaybeTrackTags = TrackTags | None
type MaybeAlbumTags = AlbumTags | None
type MaybeTags = Tags | None


class Tags(Model):
    """FFMPEG Metadata tags"""

    __match_args__ = (
        "album",
        "title",
        "composer",
        "genre",
        "copyright",
        "encoded_by",
        "language",
        "artist",
        "album_artist",
        "performer",
        "disc",
        "publisher",
        "track",
        "encoder",
        "lyrics",
        "compilation",
        "date",
        "creation_time",
        "album_sort",
        "artist_sort",
        "title_sort",
    )

    title: MaybeStr = None
    album: MaybeStr = None
    composer: MaybeStr = None
    genre: MaybeStr = None
    copyright: MaybeStr = None
    encoded_by: MaybeStr = None
    language: MaybeStr = None
    artist: MaybeStr = None
    album_artist: MaybeStr = None
    performer: MaybeStr = None
    disc: MaybeStr = None
    publisher: MaybeStr = None
    track: MaybeStr | MaybeInt = None
    encoder: MaybeStr = None
    lyrics: MaybeStr = None
    compilation: MaybeStr = None
    date: MaybeStr = None
    creation_time: MaybeStr = None
    album_sort: MaybeStr = None
    artist_sort: MaybeStr = None
    title_sort: MaybeStr = None

    def __add__(self, other: "Tags"):
        return Tags(**(other.as_dict() | self.as_dict()))

    def as_dict(self) -> dict[str, int | str]:
        return {k: v for k, v in self.__dict__.items() if v is not None}




class TrackTags(Tags):
    """FFMPEG track metadata tags"""
    title: str
    album: MaybeStr = None


class AlbumTags(Tags):
    """FFMPEG album metadata tags"""
    album: str
    title: MaybeStr = None
