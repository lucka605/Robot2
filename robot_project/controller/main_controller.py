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
        self.connected = False
        self.window = ControllerWindow()
        self.window.connect_requested.connect(self.handle_connect)
        self.window.disconnect_requested.connect(self.handle_disconnect)
        self.window.command_requested.connect(self.handle_command)
        self.window.append_log("Ready. Start the simulator, then connect to it over UDP.")

    def handle_connect(self, host: str, port: int) -> None:
        if self.connected:
            self.handle_disconnect()
            return
        self.client.configure(host, port)
        self.connected = True
        self.window.set_connected(True, host, port)
        self.window.append_log(f"UDP target set to {host}:{port}")
        self.window.show_status(f"Connected target set to {host}:{port}")

    def handle_disconnect(self) -> None:
        if not self.connected:
            return
        try:
            self.client.send("joystick:0.00:0.00")
            self.client.send("stop")
        except OSError:
            pass
        self.connected = False
        self.window.set_connected(False, self.client.host, self.client.port)
        self.window.append_log("Controller disconnected. Commands are disabled until reconnect.")
        self.window.show_status("Disconnected. Reconnect to send commands.")

    def handle_command(self, command: str) -> None:
        if not self.connected:
            self.window.show_status("Connect first to send commands.")
            return
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
