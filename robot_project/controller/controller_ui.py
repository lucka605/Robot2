from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPointF, QTimer, Qt, Signal
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
    QScrollArea,
    QSlider,
    QStatusBar,
    QStyle,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class JoystickWidget(QWidget):
    command_sent = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self.setMouseTracking(True)
        self._pressed = False
        self._vector = QPointF(0.0, 0.0)
        self._knob_offset = QPointF(0.0, 0.0)
        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._emit_current_vector)

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

        knob_center = QPointF(center.x() + self._knob_offset.x(), center.y() + self._knob_offset.y())
        painter.setBrush(QColor("#1d4ed8"))
        painter.drawEllipse(knob_center, 24, 24)

        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawLine(int(center.x()), rect.top() + 18, int(center.x()), rect.bottom() - 18)
        painter.drawLine(rect.left() + 18, int(center.y()), rect.right() - 18, int(center.y()))

        painter.setPen(QColor("#0f172a"))
        painter.drawText(rect.adjusted(0, 10, 0, 0), Qt.AlignTop | Qt.AlignHCenter, "Forward")
        painter.drawText(rect.adjusted(0, 0, 0, -10), Qt.AlignBottom | Qt.AlignHCenter, "Backward")
        painter.drawText(rect.adjusted(12, 0, 0, 0), Qt.AlignLeft | Qt.AlignVCenter, "Left")
        painter.drawText(rect.adjusted(0, 0, -12, 0), Qt.AlignRight | Qt.AlignVCenter, "Right")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._pressed = True
        self._update_vector(event.position())
        self._timer.start()
        self._emit_current_vector()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._pressed:
            return
        self._update_vector(event.position())
        self._emit_current_vector()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        del event
        self._pressed = False
        self._vector = QPointF(0.0, 0.0)
        self._knob_offset = QPointF(0.0, 0.0)
        self._timer.stop()
        self.command_sent.emit("joystick:0.00:0.00")
        self.update()

    def _update_vector(self, pos: QPointF) -> None:
        rect = self.rect().adjusted(12, 12, -12, -12)
        center = QPointF(rect.center())
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        radius = max(1.0, min(rect.width(), rect.height()) / 2 - 24)
        distance = (dx * dx + dy * dy) ** 0.5
        if distance > radius:
            scale = radius / distance
            dx *= scale
            dy *= scale
        self._vector = QPointF(dx / radius, dy / radius)
        self._knob_offset = QPointF(dx, dy)
        self.update()

    def _emit_current_vector(self) -> None:
        x = self._vector.x()
        y = self._vector.y()
        self.command_sent.emit(f"joystick:{x:.2f}:{y:.2f}")


class ControllerWindow(QMainWindow):
    connect_requested = Signal(str, int)
    disconnect_requested = Signal()
    command_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Smart Robot Controller")
        self.resize(980, 720)
        self._build_ui()
        self._apply_styles()
        self.setStatusBar(QStatusBar())
        self.show_status("Ready. Start the simulator, then connect.")

    def _build_ui(self) -> None:
        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

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

        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)
        self.log_panel.setMinimumHeight(160)
        self.log_panel.setPlaceholderText("Controller events and sent commands appear here.")

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)
        bottom_row.addWidget(self._build_arm_box(), 1)
        bottom_row.addWidget(self._build_gripper_box(), 1)
        bottom_row.addWidget(self._build_auto_box(), 1)
        root.addLayout(bottom_row)
        root.addWidget(self.log_panel)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content)
        self.setCentralWidget(scroll_area)
        self.set_controls_enabled(False)

    def _build_connect_box(self) -> QGroupBox:
        box = QGroupBox("Connect")
        layout = QGridLayout(box)
        self.ip_edit = QLineEdit("127.0.0.1")
        self.port_edit = QLineEdit("5005")
        self.connect_button = QPushButton("Connect")
        self.connect_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
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
        layout.addWidget(self._section_hint("Target endpoint and current dashboard state."))
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
        forward_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        backward_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        left_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        right_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        stop_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserStop))
        grid.addWidget(forward_button, 0, 1)
        grid.addWidget(left_button, 1, 0)
        grid.addWidget(stop_button, 1, 1)
        grid.addWidget(right_button, 1, 2)
        grid.addWidget(backward_button, 2, 1)

        self.joystick = JoystickWidget()
        self.joystick.command_sent.connect(self.command_requested.emit)
        motion_column = QVBoxLayout()
        motion_column.addWidget(self._section_hint("Buttons move in steps. The joystick streams smooth motion using the speed slider."))
        motion_column.addWidget(button_frame, 1)
        layout.addLayout(motion_column, 1)
        layout.addWidget(self.joystick, 1)
        return box

    def _build_speed_box(self) -> QGroupBox:
        box = QGroupBox("Speed")
        layout = QVBoxLayout(box)
        layout.addWidget(self._section_hint("Animation and autonomous traversal speed."))
        self.speed_value_label = QLabel("60")
        self.speed_value_label.setObjectName("speedBadge")
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
        layout.addWidget(self._section_hint("Simple arm pose control for pickup demos."))
        arm_up = self._command_button("Arm Up", "arm_up")
        arm_down = self._command_button("Arm Down", "arm_down")
        arm_up.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        arm_down.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        layout.addWidget(arm_up)
        layout.addWidget(arm_down)
        layout.addStretch(1)
        return box

    def _build_gripper_box(self) -> QGroupBox:
        box = QGroupBox("Gripper Controls")
        layout = QVBoxLayout(box)
        layout.addWidget(self._section_hint("Open to release, close to attach the object."))
        open_button = self._command_button("Open Gripper", "grip_open")
        close_button = self._command_button("Close Gripper", "grip_close")
        open_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        close_button.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        layout.addWidget(open_button)
        layout.addWidget(close_button)
        layout.addStretch(1)
        return box

    def _build_auto_box(self) -> QGroupBox:
        box = QGroupBox("Automation")
        layout = QVBoxLayout(box)
        layout.addWidget(self._section_hint("Obstacle toggle plus one-click autonomous routine."))
        self.obstacle_button = QPushButton("Obstacle Mode: OFF")
        self.obstacle_button.setCheckable(True)
        self.obstacle_button.clicked.connect(self._toggle_obstacles)
        auto_button = self._command_button("Auto Pick & Place", "auto_pick_and_place")
        auto_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        layout.addWidget(self.obstacle_button)
        layout.addWidget(auto_button)
        layout.addWidget(self._command_button("Reset Simulator", "reset_simulation"))
        clear_log_button = QPushButton("Clear Log")
        clear_log_button.setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        clear_log_button.clicked.connect(self.log_panel.clear)
        layout.addWidget(clear_log_button)
        layout.addStretch(1)
        return box

    def _command_button(self, label: str, command: str) -> QPushButton:
        button = QPushButton(label)
        button.clicked.connect(lambda: self.command_requested.emit(command))
        return button

    def _section_hint(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setObjectName("sectionHint")
        return label

    def _emit_connect(self) -> None:
        if self.connect_button.text() == "Disconnect":
            self.disconnect_requested.emit()
            return
        host = self.ip_edit.text().strip() or "127.0.0.1"
        port_text = self.port_edit.text().strip() or "5005"
        try:
            port = int(port_text)
        except ValueError:
            self.append_log(f"Invalid port: {port_text}")
            self.show_status("Port must be a number.")
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
        self.connect_button.setText("Disconnect" if connected else "Connect")
        self.connect_button.setIcon(
            self.style().standardIcon(QStyle.SP_DialogCancelButton if connected else QStyle.SP_DialogApplyButton)
        )
        self.ip_edit.setEnabled(not connected)
        self.port_edit.setEnabled(not connected)
        self.set_controls_enabled(connected)
        if not connected:
            self.obstacle_button.setChecked(False)
            self.obstacle_button.setText("Obstacle Mode: OFF")

    def append_log(self, message: str) -> None:
        self.log_panel.append(message)

    def show_status(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def set_controls_enabled(self, enabled: bool) -> None:
        for group_box in self.findChildren(QGroupBox):
            if group_box.title() != "Connect" and group_box.title() != "Session":
                group_box.setEnabled(enabled)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #f6f8fb;
                color: #0f172a;
                font-family: "Segoe UI", "Helvetica Neue", sans-serif;
                font-size: 14px;
            }
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #edf6ff, stop:1 #f8fafc);
            }
            #headerTitle {
                font-size: 30px;
                font-weight: 700;
                color: #0f172a;
            }
            #headerSubtitle {
                color: #334155;
                margin-bottom: 6px;
            }
            QGroupBox {
                border: 1px solid #d7e2ee;
                border-radius: 16px;
                margin-top: 12px;
                padding: 14px;
                background: rgba(255, 255, 255, 0.94);
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
                background: #155eef;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2b6df3;
            }
            QPushButton:checked {
                background: #0f766e;
            }
            #stopButton {
                background: #dc2626;
            }
            #statusBadge {
                background: #e0f2fe;
                border-radius: 12px;
                padding: 10px;
                color: #155eef;
                font-weight: 700;
            }
            #speedBadge {
                background: #eef2ff;
                border-radius: 12px;
                padding: 8px;
                color: #3730a3;
                font-size: 18px;
                font-weight: 700;
            }
            #sectionHint {
                color: #475569;
                font-size: 12px;
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
            QStatusBar {
                background: rgba(255, 255, 255, 0.92);
                border-top: 1px solid #d7e2ee;
                color: #334155;
            }
            """
        )
