import socket
import threading

from kazandb.parser.parser import RESPParser


class RedisServer:
    def __init__(self, host, port, parser, verbose):
        self.host = host
        self.port = port

        self._parser = RESPParser(parser)
        self._verbose = verbose

        self._db = {}

        self._sock = None

        self._verbose = False
        self._thread = None
        self._go = None
        self._make_thread()

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(1)

    def _run_server(self):
        return
        while True:
            conn, addr = self._sock.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    response = self._parser.parse(data)
                    conn.sendall(response)

    def _make_thread(self):
        """create the main thread of the server"""
        self._thread = threading.Thread(target=RedisServer._run_server, args=(self,))
        self._go = threading.Event()

    def set_verbose(self, verbose):
        """if verbose is true the sent and received packets will be logged"""
        self._verbose = verbose

    def start(self):
        """Start the server. It will handle request"""
        self._go.set()
        self._thread.start()

    def stop(self):
        """stop the server. It doesn't handle request anymore"""
        if self._thread.is_alive():
            self._go.clear()
            self._thread.join()
