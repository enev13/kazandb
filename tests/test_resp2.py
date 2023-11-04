from unittest.mock import mock_open, patch

import pytest

from kazandb.exceptions import ResponseError
from kazandb.resp2 import RESP2

resp = RESP2()


def test_decode_string():
    with patch("builtins.open", mock_open(read_data=b"+OK\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == b"OK"

    with patch("builtins.open", mock_open(read_data=b"+hello world\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == b"hello world"


def test_decode_errors():
    with patch("builtins.open", mock_open(read_data=b"-Error message\r\n")):
        with open("foo") as f:
            with pytest.raises(ResponseError):
                resp.decode(f)


def test_decode_integers():
    with patch("builtins.open", mock_open(read_data=b":1\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == 1

    with patch("builtins.open", mock_open(read_data=b":0\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == 0

    with patch("builtins.open", mock_open(read_data=b":-1\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == -1


def test_decode_bulk_strings():
    with patch("builtins.open", mock_open(read_data=b"$-1\r\n")):
        with open("foo") as f:
            assert resp.decode(f) is None

    with patch("builtins.open", mock_open(read_data=b"$6\r\nfoobar\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == b"foobar"

    with patch("builtins.open", mock_open(read_data=b"$0\r\n\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == b""


def test_decode_arrays():
    with patch("builtins.open", mock_open(read_data=b"*-1\r\n")):
        with open("foo") as f:
            assert resp.decode(f) is None

    with patch("builtins.open", mock_open(read_data=b"*1\r\n$4\r\nping\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == [b"ping"]

    with patch(
        "builtins.open",
        mock_open(read_data=b"*2\r\n$4\r\necho\r\n$11\r\nhello world\r\n"),
    ):
        with open("foo") as f:
            assert resp.decode(f) == [b"echo", b"hello world"]

    with patch(
        "builtins.open", mock_open(read_data=b"*2\r\n$3\r\nget\r\n$3\r\nkey\r\n")
    ):
        with open("foo") as f:
            assert resp.decode(f) == [b"get", b"key"]

    with patch(
        "builtins.open",
        mock_open(read_data=b"*3\r\n$3\r\nset\r\n$3\r\nkey\r\n$5\r\nvalue\r\n"),
    ):
        with open("foo") as f:
            assert resp.decode(f) == [b"set", b"key", b"value"]

    with patch("builtins.open", mock_open(read_data=b"*0\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == []


def test_decode_mixed_types():
    with patch("builtins.open", mock_open(read_data=b"*2\r\n$4\r\nping\r\n:1\r\n")):
        with open("foo") as f:
            assert resp.decode(f) == [b"ping", 1]


def test_decode_invalid_array():
    with patch("builtins.open", mock_open(read_data=b"*2\r\n$4\r\nping\r\n")):
        with open("foo") as f:
            with pytest.raises(ResponseError):
                resp.decode(f)


def test_decode_invalid_type():
    with patch(
        "builtins.open",
        mock_open(read_data=b"!2\r\n$4\r\nping\r\n$11\r\nhello world\r\n"),
    ):
        with open("foo") as f:
            with pytest.raises(ResponseError):
                resp.decode(f)


def test_encode_string():
    assert resp.encode("OK") == b"+OK\r\n"


def test_encode_integer():
    assert resp.encode(1) == b":1\r\n"
    assert resp.encode(0) == b":0\r\n"
    assert resp.encode(-1) == b":-1\r\n"


def test_encode_bulk_string():
    assert resp.encode(b"foobar") == b"$6\r\nfoobar\r\n"
    assert resp.encode(b"") == b"$0\r\n\r\n"


def test_encode_none_type():
    assert resp.encode(None) == b"$-1\r\n"


def test_encode_array():
    assert resp.encode([b"ping"]) == b"*1\r\n$4\r\nping\r\n"
    assert (
        resp.encode([b"echo", b"hello world"])
        == b"*2\r\n$4\r\necho\r\n$11\r\nhello world\r\n"
    )
    assert (
        resp.encode([b"set", b"key", b"value"])
        == b"*3\r\n$3\r\nset\r\n$3\r\nkey\r\n$5\r\nvalue\r\n"
    )


def test_encode_mixed_types():
    assert resp.encode([b"ping", 1]) == b"*2\r\n$4\r\nping\r\n:1\r\n"


def test_encode_invalid_type():
    with pytest.raises(ResponseError):
        resp.encode(1.0)

    with pytest.raises(ResponseError):
        resp.encode({})
