import tomllib
from pprint import pprint

from pytubemusic.model.user import Media

data = """
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
"""

data = tomllib.loads(data)
data = Media(**data)
pprint(data)
