import logging
import tomllib
from pathlib import Path

import typer
from typer import Argument, Option

from .audio import Album, Track
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
@log_call(on_enter="Building album from '{album_data}'", on_exit="DONE")
def make_album(
        album_data: Path = Argument(..., help="The album data"),
        out: Path = Option(
            Path("."),
            "--out", "-o",
            help="The directory album tracks will be written to. "
                 "Defaults to the album name",
        )
):
    with open(album_data, "rb") as f:
        album_data = tomllib.load(f)
    album = Album.from_url(**album_data)
    album.export(out)


@app.command(
    "track",
    help="Gets a single audio file from the "
         "video associated with the track_data file",
)
@log_call(on_enter="Building album from '{track_data}'", on_exit="DONE")
def make_track(
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
    track = Track.from_url(**track_data)
    track.export(out)


@app.command(
    "playlist",
    help="Gets tracks from the videos associated with the playlist",
)
@log_call(on_enter="Building album from '{playlist_data}'", on_exit="DONE")
def make_playlist_album(
        playlist_data: Path = Argument(..., help="The track data"),
        out: Path = Option(
            Path("."),
            "--out", "-o",
            help="The directory album tracks will be written to. "
                 "Defaults to the cwd",
        )
):
    with open(playlist_data, "rb") as f:
        playlist_data = tomllib.load(f)
    playlist = Album.from_playlist(**playlist_data)
    playlist.export(out)


app()
