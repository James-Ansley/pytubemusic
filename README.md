# PyTubeMusic

A cli that may or may not download albums from a certain website.

> PyTubeMusic is in alpha. Features are limited and significant API changes are
> expected

## Install

```
pip install pytubemusic
```

Requires [ffmpeg](https://ffmpeg.org/) to be installed on your machine.

## Usage

PyTubeMusic can download tracks in three formats:

- Tracks (Single files)
- Albums (A single video that is split up into individual tracks on an album)
- Playlists (Videos in a playlist that are downloaded as tracks on an album)

Each type of track needs a different configuration file that includes metadata.
These are described below.

Note: the term "timestamp" refers to a string of the form: "H?:M:S" – for
example: "23:55", "1:12:00", "5:03"

### Tracks

Track toml files have the following format:

```toml
url = "..."  # URL to video

start = "..."  # start timestamp (optional)
end = "..."  # end timestamp (optional)

[metadata]
title = "..."  # Track Name (required)
# Any other FFMPEG MP3 metadata tags
```

### Albums

```toml
# album_data.toml
url = "..."  # URL here

# Track data – a list of tables
# Each track needs a start time and an optional end time
# If an end time is not used the next track start time or the end of the video 
#     will be used
# The metadata "title" tag is required
# Track numbers are automatically added
tracks = [
    { start = "...", metadata = { title = "..." } },
    { start = "...", end = "...", metadata = { title = "..." } },
]

[metadata]
album = "..."  # Album name (required)
# Any other FFMPEG MP3 metadata tags
```

### Playlists

```toml
url = "..."  # URL to playlist

[metadata]
album = "..."  # Album name (required)
# Any other FFMPEG MP3 metadata tags
```

### CLI

A `pytubemusic` command will be exposed.

This has three commands: `album`, `track`, `playlist`.
Each command corresponds to one of the file types mentioned above.

The commands all take the path to a config TOML file and an optional `-o`
or `--out` option pointing to a directory to write the resulting tracks too.
(Note: albums and playlists are put into their own directory with the album
name).

For example:

```
pytubemusic album myConfig.toml -o exports
```
