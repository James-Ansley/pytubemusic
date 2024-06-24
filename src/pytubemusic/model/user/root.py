from pydantic import RootModel

from .album import Album
from .track import TrackType

__all__ = ("MediaType", "Media")

type MediaType = TrackType | Album


class Media:
    def __new__(cls, **kwargs) -> MediaType:
        # noinspection PyTypeChecker
        return RootModel[MediaType](**kwargs).root
