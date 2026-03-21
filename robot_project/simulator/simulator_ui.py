from __future__ import annotations

from typing import List, Tuple

from PySide6.QtCore import QPointF, QTimer, Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen, QPolygonF
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit, QVBoxLayout, QWidget

from algorithms.astar import AStarPlanner
from simulator.environment import EnvironmentModel
from simulator.robot import RobotState
from simulator.udp_server import UDPServer

GridPoint = Tuple[int, int]


class SimulationCanvas(QWidget):
    def __init__(self, environment: EnvironmentModel, robot: RobotState) -> None:
        super().__init__()
        self.environment = environment
        self.robot = robot
        self.setMinimumSize(
            self.environment.grid_width * self.environment.cell_size + 40,
            self.environment.grid_height * self.environment.cell_size + 40,
        )

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f8fafc"))

        self._draw_grid(painter)
        self._draw_goal(painter)
        self._draw_obstacles(painter)
        self._draw_traveled_path(painter)
        self._draw_planned_path(painter)
        self._draw_object(painter)
        self._draw_robot(painter)

    def _draw_grid(self, painter: QPainter) -> None:
        cell = self.environment.cell_size
        offset = 20
        painter.setPen(QPen(QColor("#cbd5e1"), 1))
        for x in range(self.environment.grid_width + 1):
            painter.drawLine(offset + x * cell, offset, offset + x * cell, offset + self.environment.grid_height * cell)
        for y in range(self.environment.grid_height + 1):
            painter.drawLine(offset, offset + y * cell, offset + self.environment.grid_width * cell, offset + y * cell)

    def _draw_goal(self, painter: QPainter) -> None:
        rect = self._cell_rect(self.environment.goal_position).adjusted(8, 8, -8, -8)
        painter.setBrush(QColor("#bbf7d0"))
        painter.setPen(QPen(QColor("#15803d"), 2))
        painter.drawRoundedRect(rect, 10, 10)
        painter.drawText(rect, Qt.AlignCenter, "GOAL")

    def _draw_obstacles(self, painter: QPainter) -> None:
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#94a3b8"))
        for cell in self.environment.visible_obstacles():
            painter.drawRoundedRect(self._cell_rect(cell).adjusted(6, 6, -6, -6), 8, 8)

    def _draw_traveled_path(self, painter: QPainter) -> None:
        if len(self.robot.traveled_path) < 2:
            return
        painter.setPen(QPen(QColor("#38bdf8"), 3))
        points = [self._cell_center(cell) for cell in self.robot.traveled_path]
        for start, end in zip(points, points[1:]):
            painter.drawLine(start, end)

    def _draw_planned_path(self, painter: QPainter) -> None:
        if not self.robot.current_path:
            return
        painter.setPen(QPen(QColor("#f59e0b"), 3, Qt.DashLine))
        points = [self._cell_center(self.robot.position)] + [self._cell_center(cell) for cell in self.robot.current_path]
        for start, end in zip(points, points[1:]):
            painter.drawLine(start, end)

    def _draw_object(self, painter: QPainter) -> None:
        object_cell = self.robot.position if self.robot.carrying_object else self.environment.object_position
        rect = self._cell_rect(object_cell).adjusted(14, 14, -14, -14)
        painter.setBrush(QColor("#f97316"))
        painter.setPen(QPen(QColor("#c2410c"), 2))
        painter.drawEllipse(rect)

    def _draw_robot(self, painter: QPainter) -> None:
        body_rect = self._cell_rect(self.robot.position).adjusted(8, 8, -8, -8)
        painter.setBrush(QColor("#1d4ed8"))
        painter.setPen(QPen(QColor("#0f172a"), 2))
        painter.drawRoundedRect(body_rect, 12, 12)

        center = body_rect.center()
        arrow = QPolygonF()
        if self.robot.heading == "N":
            arrow.append(center + QPointF(0, -18))
            arrow.append(center + QPointF(-10, 6))
            arrow.append(center + QPointF(10, 6))
        elif self.robot.heading == "S":
            arrow.append(center + QPointF(0, 18))
            arrow.append(center + QPointF(-10, -6))
            arrow.append(center + QPointF(10, -6))
        elif self.robot.heading == "W":
            arrow.append(center + QPointF(-18, 0))
            arrow.append(center + QPointF(6, -10))
            arrow.append(center + QPointF(6, 10))
        else:
            arrow.append(center + QPointF(18, 0))
            arrow.append(center + QPointF(-6, -10))
            arrow.append(center + QPointF(-6, 10))
        painter.setBrush(QColor("#dbeafe"))
        painter.drawPolygon(arrow)

        arm_start_x = body_rect.right()
        arm_start_y = body_rect.center().y()
        arm_extension = -18 if self.robot.arm_raised else 12
        arm_mid_x = arm_start_x + 14
        arm_mid_y = arm_start_y + arm_extension
        painter.setPen(QPen(QColor("#0f172a"), 4))
        painter.drawLine(QPointF(body_rect.center().x(), arm_start_y), QPointF(arm_mid_x, arm_mid_y))
        painter.drawLine(QPointF(arm_mid_x, arm_mid_y), QPointF(arm_mid_x + 16, arm_mid_y))

        grip_color = QColor("#16a34a") if not self.robot.gripper_closed else QColor("#dc2626")
        painter.setPen(QPen(grip_color, 4))
        painter.drawLine(QPointF(arm_mid_x + 16, arm_mid_y), QPointF(arm_mid_x + 22, arm_mid_y - 6))
        painter.drawLine(QPointF(arm_mid_x + 16, arm_mid_y), QPointF(arm_mid_x + 22, arm_mid_y + 6))

    def _cell_rect(self, cell: GridPoint) -> QRectF:
        x, y = cell
        size = self.environment.cell_size
        return QRectF(20 + x * size, 20 + y * size, size, size)

    def _cell_center(self, cell: GridPoint) -> QPointF:
        return self._cell_rect(cell).center()


class SimulatorWindow(QMainWindow):
    STATUSES = {
        "idle",
        "moving_to_object",
        "picking",
        "carrying",
        "moving_to_goal",
        "releasing",
        "completed",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Robot Pick-and-Place Simulator")
        self.resize(1200, 720)

        self.environment = EnvironmentModel()
        self.robot = RobotState()
        self.planner = AStarPlanner()
        self.server = UDPServer()

        self.canvas = SimulationCanvas(self.environment, self.robot)
        self.status_label = QLabel("State: idle")
        self.status_label.setObjectName("statusBadge")
        self.log_panel = QPlainTextEdit()
        self.log_panel.setReadOnly(True)

        self._build_ui()
        self._apply_styles()

        self.server.command_received.connect(self.handle_command)
        self.server.status_changed.connect(self.append_log)
        try:
            self.server.start()
        except OSError as exc:
            self.append_log(f"UDP server failed to start: {exc}")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(80)

        self.append_log("Simulator ready. Waiting for UDP commands.")

    def closeEvent(self, event) -> None:
        self.server.stop()
        super().closeEvent(event)

    def _build_ui(self) -> None:
        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(16)

        left_panel = QVBoxLayout()
        title = QLabel("Smart Mobile Robot Simulator")
        title.setObjectName("headerTitle")
        subtitle = QLabel("2D occupancy-grid simulation with A* planning, obstacle mode, and UDP command control.")
        subtitle.setObjectName("headerSubtitle")
        left_panel.addWidget(title)
        left_panel.addWidget(subtitle)
        left_panel.addWidget(self.canvas, 1)

        right_panel = QVBoxLayout()
        right_panel.addWidget(self.status_label)
        right_panel.addWidget(QLabel("Event Log"))
        right_panel.addWidget(self.log_panel, 1)

        details = QLabel(
            "Commands: move_forward, move_backward, turn_left, turn_right, stop, speed:<value>, "
            "arm_up, arm_down, grip_open, grip_close, obstacle_on, obstacle_off, auto_pick_and_place"
        )
        details.setWordWrap(True)
        right_panel.addWidget(details)

        root.addLayout(left_panel, 3)
        root.addLayout(right_panel, 2)
        self.setCentralWidget(central)

    def append_log(self, message: str) -> None:
        self.log_panel.appendPlainText(message)

    def handle_command(self, command: str) -> None:
        self.append_log(f"Received: {command}")
        if command.startswith("speed:"):
            self._handle_speed(command)
        elif command == "move_forward":
            self._handle_manual_move((0, -1), "N")
        elif command == "move_backward":
            self._handle_manual_move((0, 1), "S")
        elif command == "turn_left":
            self._handle_manual_move((-1, 0), "W")
        elif command == "turn_right":
            self._handle_manual_move((1, 0), "E")
        elif command == "stop":
            self.robot.cancel_auto()
            self._set_status("idle")
        elif command == "arm_up":
            self.robot.arm_raised = True
        elif command == "arm_down":
            self.robot.arm_raised = False
        elif command == "grip_open":
            self.robot.gripper_closed = False
            if self.robot.carrying_object and self.robot.position == self.environment.goal_position:
                self._release_object()
        elif command == "grip_close":
            self.robot.gripper_closed = True
            if self.robot.position == self.environment.object_position and not self.robot.carrying_object:
                self._pick_object()
        elif command == "obstacle_on":
            self.environment.set_obstacle_mode(True)
            self.append_log("Obstacle mode enabled.")
        elif command == "obstacle_off":
            self.environment.set_obstacle_mode(False)
            self.append_log("Obstacle mode disabled.")
        elif command == "auto_pick_and_place":
            self._start_auto_sequence()
        self.canvas.update()

    def _handle_speed(self, command: str) -> None:
        try:
            value = int(command.split(":", 1)[1])
        except ValueError:
            self.append_log("Invalid speed command.")
            return
        self.robot.set_speed(value)
        self.append_log(f"Speed set to {self.robot.speed_percent}")

    def _handle_manual_move(self, delta: GridPoint, heading: str) -> None:
        self.robot.cancel_auto()
        self.robot.heading = heading
        destination = (self.robot.position[0] + delta[0], self.robot.position[1] + delta[1])
        if not self.environment.in_bounds(destination):
            self.append_log("Move ignored: out of bounds.")
            return
        if destination in self.environment.blocked_cells():
            self.append_log("Move ignored: obstacle in the way.")
            return
        self.robot.manual_move(destination)
        self._set_status("idle")

    def _start_auto_sequence(self) -> None:
        if not self.robot.auto_active and self.robot.status == "completed" and not self.robot.carrying_object:
            self.append_log("Resetting object to its original pickup position for a new run.")
            self.environment.object_position = (10, 2)
        self.robot.auto_active = True
        self.robot.arm_raised = False
        self.robot.gripper_closed = False
        if self.robot.carrying_object:
            path = self._plan_to(self.environment.goal_position)
            if not path:
                return
            self.robot.enqueue_path(path, self.environment.goal_position)
            self._set_status("moving_to_goal")
            return
        path = self._plan_to(self.environment.object_position)
        if not path:
            return
        self.robot.enqueue_path(path, self.environment.object_position)
        self._set_status("moving_to_object")

    def _plan_to(self, target: GridPoint) -> List[GridPoint]:
        blocked = self.environment.blocked_cells()
        blocked.discard(self.robot.position)
        blocked.discard(target)
        path = self.planner.plan(
            self.robot.position,
            target,
            self.environment.grid_width,
            self.environment.grid_height,
            blocked,
        )
        if path:
            self.append_log(f"Planned path with {len(path)} waypoints to {target}.")
        else:
            self.append_log(f"No valid path to {target}.")
        return path

    def _tick(self) -> None:
        if self.robot.phase_ticks_remaining > 0:
            self.robot.phase_ticks_remaining -= 1
            if self.robot.phase_ticks_remaining == 0:
                self._advance_auto_phase()
            self.canvas.update()
            return

        if not self.robot.current_path:
            self.canvas.update()
            return

        steps_per_second = max(1.0, self.robot.speed_percent / 25.0)
        self.robot.step_progress += steps_per_second * 0.08
        if self.robot.step_progress < 1.0:
            return
        self.robot.step_progress = 0.0

        next_cell = self.robot.current_path.pop(0)
        self._update_heading(self.robot.position, next_cell)
        self.robot.position = next_cell
        self.robot.record_position()

        if not self.robot.current_path:
            self._on_target_reached()

        self.canvas.update()

    def _advance_auto_phase(self) -> None:
        if self.robot.status == "picking":
            self._pick_object()
            path = self._plan_to(self.environment.goal_position)
            if path:
                self.robot.enqueue_path(path, self.environment.goal_position)
                self._set_status("moving_to_goal")
            else:
                self.robot.cancel_auto()
                self._set_status("idle")
        elif self.robot.status == "releasing":
            self._release_object()
            self.robot.cancel_auto()
            self._set_status("completed")

    def _on_target_reached(self) -> None:
        if self.robot.status == "moving_to_object":
            self._set_status("picking")
            self.robot.phase_ticks_remaining = 6
            self.robot.arm_raised = False
            self.robot.gripper_closed = True
        elif self.robot.status == "moving_to_goal":
            self._set_status("releasing")
            self.robot.phase_ticks_remaining = 6
            self.robot.arm_raised = False
            self.robot.gripper_closed = False

    def _pick_object(self) -> None:
        self.robot.carrying_object = True
        self.robot.gripper_closed = True
        self.robot.arm_raised = True
        self._set_status("carrying")
        self.append_log("Object picked successfully.")

    def _release_object(self) -> None:
        self.robot.carrying_object = False
        self.robot.gripper_closed = False
        self.robot.arm_raised = False
        self.environment.object_position = self.environment.goal_position
        self.append_log("Object released in goal zone.")

    def _set_status(self, status: str) -> None:
        if status not in self.STATUSES:
            return
        self.robot.set_status(status)
        self.status_label.setText(f"State: {status}")
        self.append_log(f"State changed to {status}")

    def _update_heading(self, start: GridPoint, end: GridPoint) -> None:
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        if dx > 0:
            self.robot.heading = "E"
        elif dx < 0:
            self.robot.heading = "W"
        elif dy > 0:
            self.robot.heading = "S"
        elif dy < 0:
            self.robot.heading = "N"

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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ecfeff, stop:1 #f8fafc);
            }
            #headerTitle {
                font-size: 28px;
                font-weight: 700;
            }
            #headerSubtitle {
                color: #334155;
                margin-bottom: 8px;
            }
            #statusBadge {
                background: #dbeafe;
                border-radius: 12px;
                padding: 12px;
                font-size: 18px;
                font-weight: 700;
                color: #1d4ed8;
            }
            QPlainTextEdit {
                border: 1px solid #cbd5e1;
                border-radius: 12px;
                background: white;
                padding: 8px;
            }
            """
        )
