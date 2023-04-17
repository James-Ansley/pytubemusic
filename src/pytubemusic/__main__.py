import logging
from pathlib import Path

import cowexcept
from typer import Argument, Option, Typer

from .logutils import log_block, log_call, open_or_panic
from .track import Track
from .validation import loadf_or_panic

app = Typer(add_completion=False)

logger = logging.getLogger("pytubemusic")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


@app.command(
    "album",
    help="Gets album tracks as individual files "
         "from the video associated with the album_data file",
)
@log_call(
    on_enter="Building album from '{album_data}'",
    on_exit="\x1b[32mDONE!\x1b[0m",
    on_error="\x1b[31mProcessing Album Failed.\x1b[0m",
)
def make_album(
        album_data: Path = Argument(..., help="The album data"),
        out: Path = Option(
            Path("."),
            "--out", "-o",
            help="The directory album tracks will be written to. "
                 "Defaults to the album name",
        )
):
    prefix = "Processing Album Failed.\n"
    err_msg = f"{prefix}Cannot open `{album_data}`"
    with open_or_panic(album_data, "rb", err_msg) as f:
        err_msg = f"{prefix}Invalid Album TOML format for `{album_data}`."
        album_data = loadf_or_panic(f, "album", err_msg)
    tracks = list(Track.from_album(**album_data))
    with log_block(on_enter="Exporting Tracks"):
        for track in tracks:
            track.export(out / track.album)


@app.command(
    "track",
    help="Gets a single audio file from the "
         "video associated with the track_data file",
)
@log_call(
    on_enter="Building track from '{track_data}'",
    on_exit="\x1b[32mDONE!\x1b[0m",
    on_error="\x1b[31mProcessing Track Failed.\x1b[0m",
)
def make_track(
        track_data: Path = Argument(..., help="The track data"),
        out: Path = Option(
            Path("."),
            "--out", "-o",
            help="The directory album tracks will be written to. "
                 "Defaults to the cwd",
        )
):
    prefix = "Processing Track Failed.\n"
    err_msg = f"{prefix}Cannot open `{track_data}`"
    with open_or_panic(track_data, "rb", err_msg) as f:
        err_msg = f"{prefix}Invalid Track TOML format for `{track_data}`."
        track_data = loadf_or_panic(f, "track", err_msg)
    track = Track.from_video(**track_data)
    track.export(out)


@app.command(
    "playlist",
    help="Gets tracks from the videos associated with the playlist",
)
@log_call(
    on_enter="Building album from '{playlist_data}'",
    on_exit="\x1b[32mDONE!\x1b[0m",
    on_error="\x1b[31mProcessing Playlist Failed.\x1b[0m",
)
def make_playlist_album(
        playlist_data: Path = Argument(..., help="The track data"),
        out: Path = Option(
            Path("."),
            "--out", "-o",
            help="The directory album tracks will be written to. "
                 "Defaults to the cwd",
        )
):
    err_msg = f"Processing Playlist Failed.\nCannot open `{playlist_data}`"
    with open_or_panic(playlist_data, "rb", err_msg) as f:
        err_msg = f"Processing Playlist Failed.\nInvalid Playlist TOML format."
        playlist_data = loadf_or_panic(f, "playlist", err_msg)
    tracks = list(Track.from_playlist(**playlist_data))
    with log_block(on_enter="Exporting tracks"):
        for track in tracks:
            track.export(out / track.album)


@app.callback(invoke_without_command=True)
def main():
    cowexcept.activate()


app()
