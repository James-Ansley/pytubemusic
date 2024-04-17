import pydantic as _pydantic

from .base import *
from .album import *
from .cover import *
from .tags import *
from .track import *
from .track_data import *

type RootType = "Album | Track"
RootModel = _pydantic.RootModel[RootType]
