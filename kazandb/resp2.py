from typing import Any, BinaryIO
from .exceptions import ResponseError


CFLF = b"\r\n"


class RESP2:
    def decode(self, buff: BinaryIO) -> Any:
        """
        Decode a RESP2 message from a file-like object.

        :param buff: A file-like object.
        :return: The decoded message.
        raises: ResponseError
        """
        raw = buff.readline()
        data_type = raw[:1]
        msg = raw[1:].strip(CFLF)

        # Error
        if data_type == b"-":
            msg = msg.decode("utf-8", errors="replace")
            raise ResponseError(msg)
        # Simple string
        elif data_type == b"+":
            pass
        # Integer
        elif data_type == b":":
            msg = int(msg)
        # Null
        elif data_type == b"$" and msg == b"-1":
            return None
        # Bulk string
        elif data_type == b"$":
            msg = buff.read(int(msg) + 2).strip(CFLF)
        # Null array
        elif data_type == b"*" and msg == b"-1":
            return None
        # Bulk array
        elif data_type == b"*":
            element_count = int(msg)
            if element_count == 0:
                return []
            msg = [self.decode(buff) for _ in range(element_count)]
        else:
            raise ResponseError("Unknown response type")
        return msg

    def encode(self, msg: Any) -> bytes:
        """
        Encode a RESP2 message.

        :param msg: The message to encode.
        :return: The encoded pytmessage.
        raises: ResponseError
        """
        if isinstance(msg, bytes):
            return b"$%d\r\n%s\r\n" % (len(msg), msg)
        elif isinstance(msg, str):
            return b"+%b\r\n" % msg.encode("utf-8")
        elif isinstance(msg, int):
            return b":%d\r\n" % msg
        elif msg is None:
            return b"$-1\r\n"
        elif isinstance(msg, list):
            return b"*%d\r\n%s" % (
                len(msg),
                b"".join([self.encode(item) for item in msg]),
            )
        else:
            raise ResponseError("Unknown response type")
