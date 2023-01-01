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

Album/Track data must be provided in toml form. e.g.:

```toml
# album_data.toml
url = "..."  # URL here

[metadata]
name = "Sonatas for Two Pianos"
album = "Sonatas for Two Pianos"
artist = "Claude Bolling"
genre = "Classical"
year = 1989
tracks = [
    { time = "00:00", name = "Sonata No.1 C Minor" },
    { time = "24:00", name = "Sonata No.2 G-Sharp Minor" },
]
```

The `metadata.tracks` field specifies the name of each track and when each track
starts.

The cli can then be used to download the whole video as a single audio file, or
as individual tracks:
- `pytubemusic album album_data.toml` will download each track as a separate audio
file.  
- `pytubemusic track album_data.toml` will download the video as a single
audio file.
