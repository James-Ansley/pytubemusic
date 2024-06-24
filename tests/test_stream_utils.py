from io import BytesIO

from pytubemusic.streams.utils import stream
from tests import test


@test()
def stream_util_context_manager_will_seek_io_streams_to_0():
    with stream(BytesIO()) as buffer:
        buffer.write(b"\xFF\xFF")
        assert buffer.tell() == 2
    assert buffer.tell() == 0
