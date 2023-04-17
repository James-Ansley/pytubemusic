from datetime import timedelta

from pytubemusic.utils import to_delta, to_timestamp


def test_to_timestamp():
    assert to_timestamp(timedelta(0)) == "00:00:00.00"
    assert to_timestamp(timedelta(milliseconds=510)) == "00:00:00.51"
    assert to_timestamp(timedelta(seconds=32)) == "00:00:32.00"
    assert to_timestamp(timedelta(seconds=9)) == "00:00:09.00"
    assert to_timestamp(timedelta(minutes=17)) == "00:17:00.00"
    assert to_timestamp(timedelta(minutes=59)) == "00:59:00.00"
    assert to_timestamp(timedelta(hours=54)) == "54:00:00.00"
    assert to_timestamp(timedelta(hours=1)) == "01:00:00.00"
    assert to_timestamp(timedelta(hours=245)) == "245:00:00.00"

    duration = timedelta(hours=1, minutes=22, seconds=51, milliseconds=250)
    assert to_timestamp(duration) == "01:22:51.25"
    duration = timedelta(hours=502, minutes=1, seconds=1, milliseconds=10)
    assert to_timestamp(duration) == "502:01:01.01"


def test_to_delta():
    assert to_delta("0:01") == timedelta(seconds=1)
    assert to_delta("00:59") == timedelta(seconds=59)
    assert to_delta("1:30") == timedelta(minutes=1, seconds=30)
    assert to_delta("21:17") == timedelta(minutes=21, seconds=17)
    assert to_delta("4:00:15") == timedelta(hours=4, seconds=15)
    assert to_delta("20:05:00") == timedelta(hours=20, minutes=5)
    assert to_delta("0.75") == timedelta(milliseconds=750)
    assert to_delta("0:10.01") == timedelta(seconds=10, milliseconds=10)

    assert to_delta("00:00:00.00") == timedelta()
    assert to_delta("00:00.00") == timedelta()
    assert to_delta("00.00") == timedelta()
    assert to_delta("0.00") == timedelta()
