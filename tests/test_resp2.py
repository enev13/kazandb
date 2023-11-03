from unittest.mock import mock_open, patch

import pytest

from kazandb.exceptions import ResponseError
from kazandb.resp2 import RESP2

resp = RESP2()


def test_string():
    with patch("builtins.open", mock_open(read_data=b"+OK\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == b"OK"

    with patch("builtins.open", mock_open(read_data=b"+hello world\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == b"hello world"


def test_errors():
    with patch("builtins.open", mock_open(read_data=b"-Error message\r\n")):
        with open("foo") as f:
            with pytest.raises(ResponseError):
                resp.read_response(f)


def test_integers():
    with patch("builtins.open", mock_open(read_data=b":1\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == 1

    with patch("builtins.open", mock_open(read_data=b":0\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == 0

    with patch("builtins.open", mock_open(read_data=b":-1\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == -1


def test_bulk_strings():
    with patch("builtins.open", mock_open(read_data=b"$6\r\nfoobar\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == b"foobar"

    with patch("builtins.open", mock_open(read_data=b"$0\r\n\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == b""


def test_arrays():
    with patch("builtins.open", mock_open(read_data=b"*-1\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) is None

    with patch("builtins.open", mock_open(read_data=b"*1\r\n$4\r\nping\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == [b"ping"]

    with patch("builtins.open", mock_open(read_data=b"*2\r\n$4\r\necho\r\n$11\r\nhello world\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == [b"echo", b"hello world"]

    with patch("builtins.open", mock_open(read_data=b"*2\r\n$3\r\nget\r\n$3\r\nkey\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == [b"get", b"key"]

    with patch("builtins.open", mock_open(read_data=b"*3\r\n$3\r\nset\r\n$3\r\nkey\r\n$5\r\nvalue\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == [b"set", b"key", b"value"]


def test_mixed_types():
    with patch("builtins.open", mock_open(read_data=b"*2\r\n$4\r\nping\r\n:1\r\n")):
        with open("foo") as f:
            assert resp.read_response(f) == [b"ping", 1]


def test_invalid_array():
    with patch("builtins.open", mock_open(read_data=b"*2\r\n$4\r\nping\r\n")):
        with open("foo") as f:
            with pytest.raises(ResponseError):
                resp.read_response(f)


def test_invalid_type():
    with patch("builtins.open", mock_open(read_data=b"!2\r\n$4\r\nping\r\n$11\r\nhello world\r\n")):
        with open("foo") as f:
            with pytest.raises(ResponseError):
                resp.read_response(f)
