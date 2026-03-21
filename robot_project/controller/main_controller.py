from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controller.controller_ui import ControllerWindow
from controller.udp_client import UDPClient


class ControllerApp:
    def __init__(self) -> None:
        self.client = UDPClient()
        self.window = ControllerWindow()
        self.window.connect_requested.connect(self.handle_connect)
        self.window.command_requested.connect(self.handle_command)
        self.window.append_log("Ready. Start the simulator, then connect to it over UDP.")

    def handle_connect(self, host: str, port: int) -> None:
        self.client.configure(host, port)
        self.window.set_connected(True, host, port)
        self.window.append_log(f"UDP target set to {host}:{port}")
        self.window.show_status(f"Connected target set to {host}:{port}")

    def handle_command(self, command: str) -> None:
        try:
            self.client.send(command)
            if command.startswith("joystick:"):
                self.window.show_status("Joystick streaming active.")
            else:
                self.window.append_log(f"Sent command: {command}")
                self.window.show_status(f"Last command: {command}")
        except OSError as exc:
            self.window.append_log(f"Send failed: {exc}")
            self.window.show_status("Send failed. Check the simulator and endpoint.")


def main() -> int:
    app = QApplication(sys.argv)
    controller = ControllerApp()
    controller.window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
