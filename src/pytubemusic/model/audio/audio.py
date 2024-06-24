from dataclasses import dataclass
from pathlib import PurePath

from pydub import AudioSegment

from pytubemusic.model.user import Tags
from pytubemusic.model import MaybeIO


@dataclass(frozen=True)
class Audio:
    raw_audio: "RawAudio"
    metadata: Tags
    cover: MaybeIO

    def default_path(self) -> PurePath:
        if self.metadata.album is not None:
            return PurePath(self.metadata.album, self.metadata.title + ".mp3")
        else:
            return PurePath(self.metadata.title + ".mp3")


@dataclass(frozen=True)
class RawAudio:
    segment: AudioSegment
    bit_rate: int
