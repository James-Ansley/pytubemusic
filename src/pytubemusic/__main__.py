import logging
from collections.abc import Mapping
from pathlib import Path

import cowexcept
from typer import Argument, Option, Typer

from .logutils import log_block, log_call
from .track import Track
from .utils import get_cover, open_or_panic
from .validation import loadf_or_panic

app = Typer(add_completion=False)

logger = logging.getLogger("pytubemusic")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

CANNOT_OPEN_FILE = "Cannot open `{}`".strip()
INVALID_TOML_FORMAT = "Invalid TOML format for `{}`"


@app.command()
@log_call(
    on_enter="Loading from '{path}'",
    on_exit="\x1b[32mDONE!\x1b[0m",
    on_error="\x1b[31mProcessing Failed.\x1b[0m",
)
def main(
        path: Path = Argument(..., help="Path to track/album toml file"),
        out: Path = Option(
            Path("."),
            "--out", "-o",
            help="The directory files will be written to",
        ),
):
    cowexcept.activate()
    with open_or_panic(path, "rb", CANNOT_OPEN_FILE.format(path)) as f:
        data = loadf_or_panic(f, "type", INVALID_TOML_FORMAT.format(path))
    data |= {"cover": get_cover(data.get("cover"), path)}
    match data:
        case {"type": "album", **data}:
            make_album(data, out)
        case {"type": "track", **data}:
            make_track(data, out)


@log_call(on_enter="Building album")
def make_album(data: Mapping, out: Path):
    tracks = list(Track.from_album(**data))
    with log_block(on_enter="Exporting Tracks"):
        for track in tracks:
            track.export(out / track.album)


@log_call(on_enter="Building track")
def make_track(data: Mapping, out: Path):
    track = Track.from_track_part(**data)
    track.export(out)


app()
