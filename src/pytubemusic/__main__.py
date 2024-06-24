import json
import logging
import sys
import tomllib
from pathlib import Path
from typing import Annotated

import arguably
from pydantic import RootModel

from pytubemusic.logging import log, setup_handler
from pytubemusic.model.audio import Audio
from pytubemusic.model.track import TrackData
from pytubemusic.model.user import Album, Media, MediaType, TrackType
from pytubemusic.streams.track import fetch_track


@arguably.command
def export(
      conf: Path,
      *,
      out: Path | None = None,
      quiet: bool = False,
):
    """
    Exports the track(s) from the specified ``conf`` path.

    :param conf: The path to the configuration file specifying video data
    :param out: [-o] The directory files/folders will be exported to.
        If not given, uses the cwd.
    :param quiet: [-q] Whether logs should be suppressed
    """
    if not quiet:
        setup_handler(logging.StreamHandler(sys.stderr))

    if out is None:
        out = Path.cwd()

    with open(conf, "rb") as f:
        data = tomllib.load(f)
        media = Media(**data)
        track_data = TrackData.from_media(media)
        for track in track_data:
            log(f"Processing track: {track.metadata.title}")
            audio = fetch_track(track, context=conf.parent)
            log(f"Exporting track: {track.metadata.title}")
            export_audio(out, audio)
            log(f"Exported track: {track.metadata.title}")


# noinspection PyTypeChecker
@arguably.command
def dump_schema(
      schema: Annotated[str, arguably.arg.choices("Album", "Track", "Media")],
      *,
      out: Path,
      quiet: bool = False,
):
    """
    Exports the specified json schema to the specified directory

    :param schema: The schema to be dumped
    :param out: [-o] The directory files/folders will be exported to.
        If not given, uses the cwd.
    :param quiet: [-q] Whether logs should be suppressed
    """
    if not quiet:
        setup_handler(logging.StreamHandler(sys.stderr))

    if out is None:
        out = Path.cwd()

    if schema == "Album":
        model = RootModel[Album]
    elif schema == "Track":
        model = RootModel[TrackType]
    elif schema == "Media":
        model = RootModel[MediaType]
    else:
        raise ValueError(f"Unrecognized schema type: {schema}")
    schema_data = model.model_json_schema()
    with open(out / (schema + ".json"), "w") as f:
        json.dump(schema_data, f, indent=2)


def export_audio(root: Path, audio: Audio) -> None:
    path = Path(root, audio.default_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        audio.raw_audio.segment.export(
            f,
            tags=audio.metadata.as_dict(),
            cover=audio.cover.name if audio.cover is not None else None,
            parameters=["-b:a", f"{audio.raw_audio.bit_rate}"],
        )


def run():
    arguably.run()


if __name__ == "__main__":
    arguably.run()
