from abc import ABC, abstractmethod
from typing import Any, BinaryIO

from kazandb.exceptions import ResponseError


CFLF = b"\r\n"


class AbstractParser(ABC):
    """Abstract class for RESP parsers"""

    _name = ""

    @abstractmethod
    def encode(self):
        raise NotImplementedError

    @abstractmethod
    def decode(self):
        raise NotImplementedError

    @classmethod
    def name(cls) -> str:
        return cls._name


class RESPParser(AbstractParser):
    def __init__(self, parser_type):
        self._parser = self.identify_parser(parser_type)

    def identify_parser(self, parser_type):
        for parser in AbstractParser.__subclasses__():
            try:
                if parser.name() == parser_type:
                    return parser()
            except Exception:
                continue
        raise ValueError(f"Parser {parser_type} not found")

    def encode(self, msg):
        return self._parser.encode(msg)

    def decode(self, buff):
        return self._parser.decode(buff)


class RESP2(AbstractParser):
    _name = "resp2"

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
