import threading
import json
import queue

class BaseSession:

    def __init__(self, addr):
        self.addr = addr
        self.id = None
        self.alive = True
        self.lock = threading.Lock()

    def set_id(self, sid):
        self.id = sid

    def send(self, data):
        raise NotImplementedError

    def receive(self, timeout=None):
        raise NotImplementedError

    def check_alive(self):
        return self.alive

    def close(self):
        self.alive = False

class TCPSession(BaseSession):

    def __init__(self, conn, addr):
        super().__init__(addr)
        self.conn = conn
        self._buffer = b""
        self._result_queue = queue.Queue()
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def _recv_loop(self):
        """Continuously read from socket and queue parsed JSON messages."""
        while self.alive:
            while b"\n" in self._buffer:
                line, self._buffer = self._buffer.split(b"\n", 1)
                try:
                    msg = json.loads(line.decode(errors="ignore"))
                    self._result_queue.put(msg)
                except json.JSONDecodeError:
                    pass

            try:
                chunk = self.conn.recv(4096)
                if not chunk:
                    self.alive = False
                    return
                self._buffer += chunk
            except Exception:
                self.alive = False
                return

    def send(self, data):
        with self.lock:
            msg = json.dumps(data) + "\n"
            try:
                self.conn.sendall(msg.encode())
            except Exception:
                self.alive = False

    def receive(self, timeout=None):
        """Get next message from the receiver queue.

        Args:
            timeout: Max seconds to wait per poll cycle. None = block until
                     a message arrives or the session dies.
        """
        if timeout is not None:
            try:
                return self._result_queue.get(timeout=timeout)
            except queue.Empty:
                return None

        # No timeout — block with periodic alive checks
        while self.alive:
            try:
                return self._result_queue.get(timeout=0.5)
            except queue.Empty:
                continue
        return None

    def close(self):
        self.alive = False
        try:
            self.conn.close()
        except Exception:
            pass

class HTTPSession(BaseSession):

    def __init__(self, addr):
        super().__init__(addr)
        self.command_queue = queue.Queue()
        self.result_queue = queue.Queue()

    def send(self, data):
        self.command_queue.put(data)

    def receive(self, timeout=None):
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def close(self):
        self.alive = False
        self.send({"type": "exit"})


