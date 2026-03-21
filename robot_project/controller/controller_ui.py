from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class JoystickWidget(QWidget):
    direction_sent = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(180, 180)

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(12, 12, -12, -12)
        center = QPointF(rect.center())
        radius = min(rect.width(), rect.height()) / 2

        painter.setPen(QPen(QColor("#0f172a"), 2))
        painter.setBrush(QColor("#dbeafe"))
        painter.drawEllipse(center, radius, radius)

        painter.setBrush(QColor("#1d4ed8"))
        painter.drawEllipse(center, 24, 24)

        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawLine(int(center.x()), rect.top() + 18, int(center.x()), rect.bottom() - 18)
        painter.drawLine(rect.left() + 18, int(center.y()), rect.right() - 18, int(center.y()))

        painter.setPen(QColor("#0f172a"))
        painter.drawText(rect.adjusted(0, 10, 0, 0), Qt.AlignTop | Qt.AlignHCenter, "Forward")
        painter.drawText(rect.adjusted(0, 0, 0, -10), Qt.AlignBottom | Qt.AlignHCenter, "Backward")
        painter.drawText(rect.adjusted(12, 0, 0, 0), Qt.AlignLeft | Qt.AlignVCenter, "Left")
        painter.drawText(rect.adjusted(0, 0, -12, 0), Qt.AlignRight | Qt.AlignVCenter, "Right")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        direction = self._direction_from_pos(event.position())
        if direction:
            self.direction_sent.emit(direction)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        del event
        self.direction_sent.emit("stop")

    def _direction_from_pos(self, pos: QPointF) -> str:
        center = self.rect().center()
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        if abs(dx) > abs(dy):
            return "turn_right" if dx > 0 else "turn_left"
        return "move_backward" if dy > 0 else "move_forward"


class ControllerWindow(QMainWindow):
    connect_requested = Signal(str, int)
    command_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Smart Robot Controller")
        self.resize(980, 720)
        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        header = QLabel("Smart Mobile Robot Controller")
        header.setObjectName("headerTitle")
        subtitle = QLabel("UDP dashboard for mobile motion, arm commands, gripper control, and autonomous pick-and-place.")
        subtitle.setObjectName("headerSubtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)
        top_row.addWidget(self._build_connect_box(), 1)
        top_row.addWidget(self._build_status_box(), 1)
        root.addLayout(top_row)

        middle_row = QHBoxLayout()
        middle_row.setSpacing(16)
        middle_row.addWidget(self._build_motion_box(), 2)
        middle_row.addWidget(self._build_speed_box(), 1)
        root.addLayout(middle_row)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)
        bottom_row.addWidget(self._build_arm_box(), 1)
        bottom_row.addWidget(self._build_gripper_box(), 1)
        bottom_row.addWidget(self._build_auto_box(), 1)
        root.addLayout(bottom_row)

        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)
        self.log_panel.setMinimumHeight(160)
        root.addWidget(self.log_panel)

        self.setCentralWidget(central)

    def _build_connect_box(self) -> QGroupBox:
        box = QGroupBox("Connect")
        layout = QGridLayout(box)
        self.ip_edit = QLineEdit("127.0.0.1")
        self.port_edit = QLineEdit("5005")
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._emit_connect)
        layout.addWidget(QLabel("IP Address"), 0, 0)
        layout.addWidget(self.ip_edit, 0, 1)
        layout.addWidget(QLabel("Port"), 1, 0)
        layout.addWidget(self.port_edit, 1, 1)
        layout.addWidget(self.connect_button, 2, 0, 1, 2)
        return box

    def _build_status_box(self) -> QGroupBox:
        box = QGroupBox("Session")
        layout = QVBoxLayout(box)
        self.connection_label = QLabel("Disconnected")
        self.connection_label.setObjectName("statusBadge")
        layout.addWidget(QLabel("Connection Status"))
        layout.addWidget(self.connection_label)
        layout.addStretch(1)
        return box

    def _build_motion_box(self) -> QGroupBox:
        box = QGroupBox("Movement Controls")
        layout = QHBoxLayout(box)
        layout.setSpacing(16)

        button_frame = QFrame()
        grid = QGridLayout(button_frame)
        grid.setSpacing(10)
        forward_button = self._command_button("Forward", "move_forward")
        backward_button = self._command_button("Backward", "move_backward")
        left_button = self._command_button("Left", "turn_left")
        right_button = self._command_button("Right", "turn_right")
        stop_button = self._command_button("Stop", "stop")
        stop_button.setObjectName("stopButton")
        grid.addWidget(forward_button, 0, 1)
        grid.addWidget(left_button, 1, 0)
        grid.addWidget(stop_button, 1, 1)
        grid.addWidget(right_button, 1, 2)
        grid.addWidget(backward_button, 2, 1)

        self.joystick = JoystickWidget()
        self.joystick.direction_sent.connect(self.command_requested.emit)
        layout.addWidget(button_frame, 1)
        layout.addWidget(self.joystick, 1)
        return box

    def _build_speed_box(self) -> QGroupBox:
        box = QGroupBox("Speed")
        layout = QVBoxLayout(box)
        self.speed_value_label = QLabel("60")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(10, 100)
        self.speed_slider.setValue(60)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        layout.addWidget(QLabel("Robot Speed"))
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.speed_value_label)
        layout.addStretch(1)
        return box

    def _build_arm_box(self) -> QGroupBox:
        box = QGroupBox("Arm Controls")
        layout = QVBoxLayout(box)
        layout.addWidget(self._command_button("Arm Up", "arm_up"))
        layout.addWidget(self._command_button("Arm Down", "arm_down"))
        layout.addStretch(1)
        return box

    def _build_gripper_box(self) -> QGroupBox:
        box = QGroupBox("Gripper Controls")
        layout = QVBoxLayout(box)
        layout.addWidget(self._command_button("Open Gripper", "grip_open"))
        layout.addWidget(self._command_button("Close Gripper", "grip_close"))
        layout.addStretch(1)
        return box

    def _build_auto_box(self) -> QGroupBox:
        box = QGroupBox("Automation")
        layout = QVBoxLayout(box)
        self.obstacle_button = QPushButton("Obstacle Mode: OFF")
        self.obstacle_button.setCheckable(True)
        self.obstacle_button.clicked.connect(self._toggle_obstacles)
        auto_button = self._command_button("Auto Pick & Place", "auto_pick_and_place")
        layout.addWidget(self.obstacle_button)
        layout.addWidget(auto_button)
        layout.addStretch(1)
        return box

    def _command_button(self, label: str, command: str) -> QPushButton:
        button = QPushButton(label)
        button.clicked.connect(lambda: self.command_requested.emit(command))
        return button

    def _emit_connect(self) -> None:
        host = self.ip_edit.text().strip() or "127.0.0.1"
        port_text = self.port_edit.text().strip() or "5005"
        try:
            port = int(port_text)
        except ValueError:
            self.append_log(f"Invalid port: {port_text}")
            return
        self.connect_requested.emit(host, port)

    def _on_speed_changed(self, value: int) -> None:
        self.speed_value_label.setText(str(value))
        self.command_requested.emit(f"speed:{value}")

    def _toggle_obstacles(self, checked: bool) -> None:
        self.obstacle_button.setText("Obstacle Mode: ON" if checked else "Obstacle Mode: OFF")
        self.command_requested.emit("obstacle_on" if checked else "obstacle_off")

    def set_connected(self, connected: bool, host: str, port: int) -> None:
        self.connection_label.setText(f"Connected to {host}:{port}" if connected else "Disconnected")

    def append_log(self, message: str) -> None:
        self.log_panel.append(message)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #f8fafc;
                color: #0f172a;
                font-family: "Segoe UI", "Helvetica Neue", sans-serif;
                font-size: 14px;
            }
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0f2fe, stop:1 #f8fafc);
            }
            #headerTitle {
                font-size: 28px;
                font-weight: 700;
                color: #0f172a;
            }
            #headerSubtitle {
                color: #334155;
                margin-bottom: 6px;
            }
            QGroupBox {
                border: 1px solid #cbd5e1;
                border-radius: 14px;
                margin-top: 12px;
                padding: 14px;
                background: rgba(255, 255, 255, 0.85);
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            QPushButton {
                border: none;
                border-radius: 12px;
                padding: 10px 14px;
                background: #1d4ed8;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:checked {
                background: #0f766e;
            }
            #stopButton {
                background: #dc2626;
            }
            #statusBadge {
                background: #dbeafe;
                border-radius: 10px;
                padding: 10px;
                color: #1d4ed8;
                font-weight: 700;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                padding: 8px;
                background: white;
            }
            QSlider::groove:horizontal {
                height: 8px;
                border-radius: 4px;
                background: #cbd5e1;
            }
            QSlider::handle:horizontal {
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
                background: #0f172a;
            }
            """
        )
