from __future__ import annotations

import socket
from dataclasses import dataclass


@dataclass
class UDPClient:
    host: str = "127.0.0.1"
    port: int = 5005

    def __post_init__(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def configure(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def send(self, message: str) -> None:
        self._socket.sendto(message.encode("utf-8"), (self.host, self.port))
