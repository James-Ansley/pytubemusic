# PyTubeMusic

A cli that may or may not download music from a certain website.

## Install

```
pip install pytubemusic
```

**Requires [ffmpeg](https://ffmpeg.org/) to be installed on your machine.**

<details>
<summary>Installation Note</summary>

PyTubeMusic uses the [PyTube](https://github.com/pytube/pytube) library. This
can occasionally break. However, patches are usually quickly released as new
versions or as pull requests. Try upgrading to the latest version of PyTube if
downloading fails.

> Note, to pip install from a pull request do:
> ```text
>  pip install git+https://github.com/pytube/pytube.git@refs/pull/<PR_NUM>/head
> ```
> Where `<PR_NUM>` is the number of the pull request.

</details>

## Usage

PyTubeMusic track data is specified in TOML formats. TOML files have the
following format:

```toml
type = "track | album"

cover = { url = "URL" }
#cover = { file = "Path" }

# For "track" type only
url = "..."  # URL to video
start = "..."  # start timestamp for track (optional - default 00:00)
end = "..."  # end timestamp for track (optional - default end of video)

[metadata]
album = "..."  # Required for "album" type
title = "..."  # required for "track" type
# Other FFMPEG metadata tags (unchecked)


# For album type only – array of track types
[[tracks]]
# Tracks data format specified below
```

### Album `tracks` blocks

For albums, several different track blocks can be specified. These are:

- `track` - a single track from a video:
  ```toml
  [[tracks]]
  type = "track"
  url = "..."  # URL to video
  start = "..."  # start timestamp (optional - default 00:00)
  end = "..."  # end timestamp(optional - default end of video)
  
  [tracks.metadata]
  title = "..." # required for "track" type
  # Other FFMPEG metadata tags (unchecked)
  ```
- `split` - several tracks from a single video:
  ```toml
  [[tracks]]
  type = "split"
  url = "..."  # URL to video
  tracks = [
    { start = "...", end = "...", metadata = { title = "..." } },
  ]
  ```
  start and end timestamps in track list are optional - start defaults to 00:00
  and end defaults to the start of the next track or the end of the video. The
  metadata title is required – other ffmpeg metadata tags can be added which
  will override album-wide metadata.
- `merge` - combines multiple videos into one track
  ```toml
  [[tracks]]
  type = "merge"
  tracks = [
    {url = "...", start = "...", end = "..."},
  ]
  [tracks.metadata]
  title = "..." # required
  # Other FFMPEG metadata tags (unchecked)
  ```
  start and end timestamps in track list are optional - start defaults to 00:00
  and end defaults to the start of the next track or the end of the video.
- `playlist` - downloads a playlist - as either several tracks or combined into
  one.
  ```toml
  [[tracks]]
  type = "playlist"
  join = false  # whether to join videos into single track (optional, default false)
  tracks = [
    # include metadata only if join = false
    {start = "...", end = "...", drop = false, metadata = {title = "..."}},
  ]

  # include only if join is true
  [tracks.metadata]
  title = "..."
  ```
  Metadata needs to be included on tracks only if join is false, and for the
  overall track if join is true. The `drop` boolean on each track specifies
  whether that video should be ignored from the playlist videos. start and end
  timestamps are optional.

### CLI

A `pytubemusic` command will be added upon installation. The help for the CLI
is:

```text
Usage: pytubemusic [OPTIONS] PATH

Arguments
 * path PATH Path to track/album toml file [required]

Options
 --out -o PATH The directory files will be written to [default: .]
 --help Show this message and exit.
```

Tracks are written to the cwd unless `--out` is specified, albums are written to
a directory with the album name within the `--out` directory.
