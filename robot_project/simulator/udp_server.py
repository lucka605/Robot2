from __future__ import annotations

import socket
import threading
from typing import Optional

from PySide6.QtCore import QObject, Signal


class UDPServer(QObject):
    command_received = Signal(str)
    status_changed = Signal(str)

    def __init__(self, host: str = "127.0.0.1", port: int = 5005) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self._socket: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self.host, self.port))
        self._socket.settimeout(0.5)
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()
        self.status_changed.emit(f"Listening on {self.host}:{self.port}")

    def stop(self) -> None:
        self._running = False
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def _listen(self) -> None:
        while self._running and self._socket is not None:
            try:
                data, _ = self._socket.recvfrom(2048)
            except socket.timeout:
                continue
            except OSError:
                break
            message = data.decode("utf-8").strip()
            if message:
                self.command_received.emit(message)
