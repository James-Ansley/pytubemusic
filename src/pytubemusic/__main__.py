import logging
import tomllib
from pathlib import Path

import typer
from typer import Argument

from .logutils import log_call
from .audio import Audio

app = typer.Typer(add_completion=False)

logger = logging.getLogger("yourtubemusic")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


@app.command(
    "album",
    help="Gets album tracks as individual files "
         "from the video associated with the album_data file",
)
@log_call(on_enter="Getting album from {album_data}", on_exit="Done!")
def album(album_data: Path = Argument(..., help="The album data")):
    with open(album_data, "rb") as f:
        album_data = tomllib.load(f)
    audio = Audio.from_url(**album_data)
    tracks = audio.split_to_tracks()
    for track in tracks:
        track.export()


@app.command(
    "track",
    help="Gets a single audio file from the "
         "video associated with the track_data file",
)
@log_call(on_enter="Getting track from {track_data}", on_exit="Done!")
def track(track_data: Path = Argument(..., help="The track data")):
    with open(track_data, "rb") as f:
        track_data = tomllib.load(f)
    audio = Audio.from_url(**track_data)
    audio.export(out=Path("."))


app()
