from pathlib import Path
from urllib.request import urlopen

uri = Path("./data/ldots.png").resolve().as_uri()
print(uri)
with urlopen(uri) as f:
    data = f.read()

with open("data/new.png", "wb") as f:
    f.write(data)
