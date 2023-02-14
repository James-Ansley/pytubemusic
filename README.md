# PyTubeMusic

A cli that may or may not download albums from a certain website.

> PyTubeMusic is in alpha. Features are limited and significant API changes are
> expected

## Install

```
pip install pytubemusic
```

**Requires [ffmpeg](https://ffmpeg.org/) to be installed on your machine.**

## Usage

PyTubeMusic can download tracks in three formats:

- Tracks (Single files)
- Albums (A single video that is split up into individual tracks on an album)
- Playlists (Videos in a playlist that are downloaded as tracks on an album)

Each type of track needs a different configuration file that includes metadata.
These are described below.

Note: the term "timestamp" refers to a string of the form: "H?:M:S.f?" – for
example: "23:55.75", "1:12:00", "5:03", "17:00.5"

### Tracks

> A single video downloaded as a track

Track toml files have the following format:

```toml
url = "..."  # URL to video

cover = "..."  # Track cover jpg URL (optional – uses thumbnail by default)

start = "..."  # start timestamp (optional)
end = "..."  # end timestamp (optional)

[metadata]
title = "..."  # Track Name (required)
# Any other FFMPEG MP3 metadata tags
```

### Albums

> A single video that is split into separate tracks on an album

Albums require a `track_data` list that defines track-specific data.
`track_data` is a list of tables that includes:

- `start` a start time stamp defining when the track starts in the video
- `end` an optional end time stamp – if not provided the start of the next track
  will be used of the end of the video in the case of the last track
- `metadata` a table of track-specific metadata – the `title` tag is required.
  Track specific metadata overwrites album metadata. Track numbers are
  automatically filled but can be manually added.

```toml
# album_data.toml
url = "..."  # URL here

cover = "..."  # Track cover jpg URL (optional – uses thumbnail by default)

track_data = [
    { start = "...", metadata = { title = "..." } },
    { start = "...", end = "...", metadata = { title = "..." } },
]

[metadata]
album = "..."  # Album name (required)
# Any other FFMPEG MP3 metadata tags
```

### Playlists

> A playlist of album tracks

For playlists, `track_data` is optional. If provided it must be provided for all
tracks in the playlist. It has the same format as album `track_data`. If not
provided, the title of each video will be used for each track title.

```toml
url = "..."  # URL to playlist

cover = "..."  # Track cover jpg URL (optional – uses thumbnails by default)

# Optional track data
track_data = [
    ...
]

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
(Note: albums and playlists are put into their own subdirectory with the album
name under the out directory).

For example:

```
pytubemusic album myConfig.toml -o exports
```
