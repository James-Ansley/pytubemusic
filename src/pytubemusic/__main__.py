import logging
import os
import tomllib
from pathlib import Path

import typer
from typer import Argument, Option

from .audio import Audio
from .logutils import log_call

app = typer.Typer(add_completion=False)

logger = logging.getLogger("pytubemusic")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


@app.command(
    "album",
    help="Gets album tracks as individual files "
         "from the video associated with the album_data file",
)
@log_call(on_enter="Getting album from {album_data}", on_exit="Done!")
def album(
        album_data: Path = Argument(..., help="The album data"),
        out: Path = Option(
            None,
            "--out", "-o",
            help="The directory album tracks will be written to. "
                 "Defaults to the album name",
        )
):
    with open(album_data, "rb") as f:
        album_data = tomllib.load(f)
    audio = Audio.from_url(**album_data)
    tracks = audio.split_to_tracks()
    if out is None:
        out = Path(audio.metadata["album"])
    os.makedirs(out, exist_ok=True)
    for track in tracks:
        track.export(out)


@app.command(
    "track",
    help="Gets a single audio file from the "
         "video associated with the track_data file",
)
@log_call(on_enter="Getting track from {track_data}", on_exit="Done!")
def track(
        track_data: Path = Argument(..., help="The track data"),
        out: Path = Option(
            Path("."),
            "--out", "-o",
            help="The directory album tracks will be written to. "
                 "Defaults to the cwd",
        )
):
    with open(track_data, "rb") as f:
        track_data = tomllib.load(f)
    audio = Audio.from_url(**track_data)
    os.makedirs(out, exist_ok=True)
    audio.export(out)


app()