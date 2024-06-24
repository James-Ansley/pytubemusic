# PyTubeMusic

A cli that may or may not download albums from a certain website.

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

`pytubemusic` has two commands:

- `export`: fetches and exports tracks specified by a TOML file
  ```
  pytubemusic export -h
  usage: pytubemusic export [-h] [-o OUT] [-q] conf
  
  Exports the track(s) from the specified ``conf`` path.
  
  positional arguments:
    conf           The path to the configuration file specifying video data
                   (type: Path)
  
  options:
    -h, --help     show this help message and exit
    -o, --out OUT  The directory files/folders will be exported to.
                   If not given, uses the cwd. (type: Path, default: None)
    -q, --quiet    Whether logs should be suppressed
                   (type: bool, default: False)
  ```

- `dump-schema`: dumps the JSON schema for Tracks and Albums to a file
  ```
  usage: pytubemusic dump-schema [-h] [-o OUT] [-q] {Album,Track,Media}
  
  Exports the specified json schema to the specified directory
  
  positional arguments:
    {Album,Track,Media}  The schema to be dumped (type: str)
  
  options:
    -h, --help           show this help message and exit
    -o, --out OUT        The directory files/folders will be exported to.
                         If not given, uses the cwd. (type: Path)
    -q, --quiet          Whether logs should be suppressed
                         (type: bool, default: False)
  ```

The primary command is `export` this requires TOML files that specifies the
URL, cover image, and other metadata for one or more tracks. The TOML format
will be described below.

### Media

There are three data types that pytubemusic can parse:

- `Media`: A union type, either an `Album`, or `Track`
- `Album`: A container for `Track`s with additional metadata
- `Track`: A specification for one or more individual tracks

It is recommended you export the `Media` json schema to use when writing TOML
files.

All media types rely on some basic primitives:

#### Data Primitives

By convention, optional fields are prefixed with `Maybe`

##### Tags

Tags come in three forms: `Tags`, `TrackTags`, `AlbumTags`.
A `Tags` object is a mapping of ffmpeg mp3 metadata tag names
(<https://wiki.multimedia.cx/index.php?title=FFmpeg_Metadata#MP3>) to their
values. The only difference between the three types of tags is that for
`TrackTags` the `title` field is required, and for `AlbumTags`, the `album`
field is required.

##### Covers

Covers are used for the track cover photos. They have two forms:
`File`, and `Url`.

`File` covers have the form:

```
path: Path
```

When resolving the `path` specified in a `File` cover, the path will be taken
as relative to the TOML config file it is specified in — unless the path
is absolute.

`Url` covers have the form:

```
href: str
```

If a URL scheme is not provided, it defaults to HTTPS

##### TimeDeltas

TimeDeltas are used to specify timestamps for tracks.
These are strings of the form: `HH:MM:SS` or `HH:MM:SS.D{1,6}`

### Tracks

There are several types of tracks:

#### Single

A single specifies a single track taken from a single URL.
It has the general form:

```
url: str = Field(pattern=r"/watch\?v=")
metadata: TrackTags
cover: MaybeCover = None
start: MaybeTimedelta = None
end: MaybeTimedelta = None
```

If the start and end timestamps are not provided, they default to the start
and end of the video respectively.

For example:

```toml
url = "https://www.example.com/watch?v=123456789"
start = "00:00:01"
end = "00:07:23.5"

[metadata]
title = "My Track"
artist = "Joe Schmoe"

[cover]
href = "https://www.example.com/pic.jpeg"
```

#### Split

A split track is where a single video is split into several smaller
audio tracks. It has the general form:

```
url: str = Field(pattern=r"/watch\?v=")
cover: MaybeCover = None
tracks: tuple[TrackStub, ...] = Field(min_length=1)
```

Where tracks is a list of one or more TrackStubs of the form:

```
metadata: TrackTags
cover: MaybeCover = None
start: MaybeTimedelta = None
end: MaybeTimedelta = None
```

If the start timestamp is not provided, it defaults to the start of the video.
If the end timestamp is not provided, it defaults to the start of the next
video, or the end of the video.

If a cover is provided in the TrackStub, it overrides any cover specified in
the Split track.

For example:

```toml
url = "https://www.example.com/watch?v=123456789"

[cover]
path = "./covers/pic1.jpeg"

[[tracks]]
start = "00:00:01"

[tracks.cover]
path = "./covers/pic2.jpeg"

[tracks.metadata]
title = "My First Track"

[[tracks]]
start = "00:07:23.5"

[tracks.metadata]
title = "My Second Track"
```

#### Playlist

Playlists download tracks from a playlist, either by merging several tracks
into one, or as separate tracks. Playlist tracks have the general form:

```
url: str = Field(pattern=r"/playlist\?list=")
cover: MaybeCover = None
tracks: tuple[TrackStub | MergeStub | Drop, ...] = ()
```

Where tracks is a list of any conbination of `TrackStub`s, `MergeStub`s, or
`Drop` literals. Videos are loaded in the order they appear in the playlist.

##### `TrackStub`s

Track stubs contain metadata about the track at that position, as well as an
optional cover and start and end timestamps:

```
metadata: TrackTags
cover: MaybeCover = None
start: MaybeTimedelta = None
end: MaybeTimedelta = None
```

##### `MergeStubs`

Merge stubs consist of track metadata, an optional cover, and a list of start
and end timestamps. For example, if the merge stub contains three time stubs,
then the next three videos from the playlist are merged into a single track.

```
metadata: TrackTags
cover: MaybeCover = None
parts: tuple[TimeStub | Drop, ...]
```

With `TimeStub`s being of the form:

```
start: MaybeTimedelta = None
end: MaybeTimedelta = None
```

##### `Drop`

A drop literal indicates a particular playlist video should be ignored:

```
drop: Literal[True] = True
```

##### Playlist Example

Here is a playlist example demonstrating various track types:

```toml
url = "www.example.com/playlist?list=123456789"
cover = {href = "www.example.com/pic.png"}

# TrackStub
[[tracks]]
start = "00:00:01"
end = "00:07:23.4"

[tracks.metadata]
title = "My First Track Title"

# Drop
[[tracks]]
drop = true

# MergeStub
[[tracks]]
parts = [{start = "00:00:05"}, {drop = true}, {}]

[tracks.metadata]
title = "My Second Track Title"
```

#### Merge

Merge tracks are used to join two or more videos into a single track.
They have the general form:

```
metadata: TrackTags
cover: MaybeCover = None
parts: tuple[AudioStub, ...] = Field(min_length=1)
```

Where `AudioStubs` are of the form:

```
url: str = Field(pattern=r"/watch\?v=")
start: MaybeTimedelta = None
end: MaybeTimedelta = None
```

For example:

```toml
[metadata]
title = "My Track"
artist = "Joe Schmoe"

[cover]
href = "https://www.example.com/pic.jpeg"

[[parts]]
url = "https://www.example.com/watch?v=123456789"
start = "00:00:01"
end = "00:07:23.5"

[[parts]]
url = "https://www.example.com/watch?v=987654321"
start = "00:00:05.2"
end = "00:15:40"
```

### Albums

Albums are just collections of tracks that have some universal metadata applied.
Album tracks will be given a `track` metadata tag denoting their position in
the album.
They have the general form:

```
metadata: AlbumTags
cover: MaybeCover = None
tracks: tuple[TrackType, ...] = Field(min_length=1)
```

Where `TrackType` is any of the above track types.

For example:

```toml
[metadata]
album = "My Album"
artist = "Joe Schmoe"

[cover]
href = "www.example.com/pic.jpg"

# Single
[[tracks]]
url = "https://www.example.com/watch?v=123456789"
start = "00:00:01"
end = "00:07:23.5"

[tracks.metadata]
title = "My Track"

# merge
[[tracks]]
[tracks.metadata]
title = "My Other Track"

[[tracks.parts]]
url = "https://www.example.com/watch?v=123456789"
start = "00:00:01"
end = "00:07:23.5"

[[tracks.parts]]
url = "https://www.example.com/watch?v=987654321"
start = "00:00:05.2"
end = "00:15:40"
```
