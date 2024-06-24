from functools import reduce
from pathlib import Path

from pytubemusic.model.audio import Audio, RawAudio
from pytubemusic.model.track import TrackData
from pytubemusic.streams.audio import fetch_audio_data
from pytubemusic.streams.images import fetch_cover_data


def fetch_track(track: TrackData, context: Path = None) -> Audio:
    return Audio(
        raw_audio=reduce(
            merge_audio,
            (fetch_audio_data(part) for part in track.parts),
        ),
        metadata=track.metadata,
        cover=fetch_cover_data(track.cover, context),
    )


def merge_audio(audio1: RawAudio, audio2: RawAudio) -> RawAudio:
    return RawAudio(
        segment=audio1.segment + audio2.segment,
        bit_rate=max(audio1.bit_rate, audio2.bit_rate),
    )
