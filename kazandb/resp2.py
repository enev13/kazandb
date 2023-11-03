from typing import BinaryIO
from .exceptions import ResponseError


class RESP2:
    def read_response(self, buff: BinaryIO):
        """
        Read a RESP2 response from a file-like object.
        """
        # Read the first byte of the response.
        # This is the type of the response.
        raw = buff.readline()
        resp_type = raw[:1]
        response = raw[1:].strip()

        # Error
        if resp_type == b"-":
            response = response.decode("utf-8", errors="replace")
            raise ResponseError(response)
        # Simple string
        elif resp_type == b"+":
            pass
        # Integer
        elif resp_type == b":":
            response = int(response)
        # Null
        elif resp_type == b"$" and response == b"-1":
            return None
        # Bulk string
        elif resp_type == b"$":
            response = buff.read(int(response) + 2).strip(b"\r\n")
        # Null array
        elif resp_type == b"*" and response == b"-1":
            return None
        # Bulk array
        elif resp_type == b"*":
            element_count = int(response)
            if element_count == 0:
                return
            response = [self.read_response(buff) for _ in range(element_count)]
        else:
            raise ResponseError("Unknown response type")
        return response
