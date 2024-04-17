import enum
import logging
import sys
from pathlib import PurePath, Path
from typing import Literal

import arguably
from pipe_utils.override import *

from pytubemusic.model import *
from pytubemusic.utils.funcs import kwarged
from pytubemusic.utils.logs import LogLevel, setup_handler


class Fmt(enum.Enum):
    TOML = "TOML"
    JSON = "JSON"
    Auto = "AUTO"


@arguably.command
def pytubemusic(
        config: PurePath,
        *,
        out: PurePath | None = None,
        fmt: Fmt | None = Fmt.Auto,
        quiet: bool = False,
        log: LogLevel = LogLevel.INFO,
):
    """
    Exports the track(s) from the specified ``config`` file.

    :param config: The path to the configuration file specifying video data
    :param out: [-o] The directory files/folders will be exported to.
        If not given, uses the cwd.
    :param fmt: [-f] The format of the conf file (either "JSON" or "TOML").
        If not given, the format is inferred from the file extension.
    :param quiet: [-q] Whether logs should be suppressed
    :param log: The log level if not quiet
    """
    if not quiet:
        setup_handler(logging.StreamHandler(sys.stderr), log)

    with open(config, "rb") as f: (
            Pipe >> f
            | get_parser >> config >> fmt
            | kwarged >> RootModel
            | it.root
            | case_when >> {
                instance_of >> Album: parse_album,
                instance_of >> Track: parse_track,
              }
            | for_each >> (export >> (out or Path.cwd()))
    ).get()


def parse_album(album):
    ...

def parse_track(track):
    ...


@curry
def get_parser(
      conf: PurePath,
      fmt: Literal["JSON", "TOML", "AUTO"],
) -> Loader[bytes, dict[str, Any]]:
    if fmt is None and conf.suffix not in (".json", ".toml"):
        panic("\n".join((
            "The type of the config path cannot be determined as JSON or TOML.",
            "Use a suffix (.toml or .json) or specify the --fmt option.",
        )))
    elif fmt == Fmt.JSON or conf.suffix == ".json":
        return json.load
    elif fmt == Fmt.TOML or conf.suffix == ".toml":
        return tomllib.load
    else:
        panic(
            "An unrecognized error occurred while "
            "determining the `conf` filetype."
        )


@curry
def export(root: PurePath, track_: "Track") -> None:
    path = track.path >> root >> track_
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        track.export >> f >> track_


if __name__ == "__main__":
    arguably.run()