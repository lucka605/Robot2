from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

GridPoint = Tuple[int, int]
FloatPoint = Tuple[float, float]


@dataclass
class RobotState:
    position: GridPoint = (1, 7)
    manual_position: FloatPoint = (1.0, 7.0)
    speed_percent: int = 60
    heading: str = "E"
    arm_raised: bool = True
    gripper_closed: bool = False
    carrying_object: bool = False
    status: str = "idle"
    current_path: List[GridPoint] = field(default_factory=list)
    traveled_path: List[GridPoint] = field(default_factory=lambda: [(1, 7)])
    target_position: Optional[GridPoint] = None
    auto_active: bool = False
    phase_ticks_remaining: int = 0
    step_progress: float = 0.0
    joystick_vector: FloatPoint = (0.0, 0.0)
    effect_label: str = ""
    effect_ticks: int = 0

    def set_status(self, status: str) -> None:
        self.status = status

    def set_speed(self, value: int) -> None:
        self.speed_percent = max(10, min(100, value))

    def reset_paths(self) -> None:
        self.current_path = []
        self.step_progress = 0.0

    def cancel_auto(self) -> None:
        self.auto_active = False
        self.phase_ticks_remaining = 0
        self.target_position = None
        self.reset_paths()

    def enqueue_path(self, path: List[GridPoint], target: GridPoint) -> None:
        self.manual_position = (float(self.position[0]), float(self.position[1]))
        self.current_path = path[1:] if len(path) > 1 else []
        self.target_position = target
        self.step_progress = 0.0

    def record_position(self) -> None:
        if not self.traveled_path or self.traveled_path[-1] != self.position:
            self.traveled_path.append(self.position)

    def manual_move(self, destination: GridPoint) -> None:
        self.position = destination
        self.manual_position = (float(destination[0]), float(destination[1]))
        self.record_position()

    def render_position(self) -> FloatPoint:
        if self.current_path:
            next_cell = self.current_path[0]
            progress = max(0.0, min(1.0, self.step_progress))
            return (
                self.position[0] + (next_cell[0] - self.position[0]) * progress,
                self.position[1] + (next_cell[1] - self.position[1]) * progress,
            )
        return self.manual_position

    def trigger_effect(self, label: str, ticks: int = 16) -> None:
        self.effect_label = label
        self.effect_ticks = ticks

    def set_joystick_vector(self, x: float, y: float) -> None:
        self.joystick_vector = (x, y)

    def joystick_active(self) -> bool:
        return abs(self.joystick_vector[0]) > 1e-6 or abs(self.joystick_vector[1]) > 1e-6

    def sync_grid_from_manual(self) -> None:
        cell = (int(round(self.manual_position[0])), int(round(self.manual_position[1])))
        if cell != self.position:
            self.position = cell
            self.record_position()

    def reset(self) -> None:
        self.position = (1, 7)
        self.manual_position = (1.0, 7.0)
        self.speed_percent = 60
        self.heading = "E"
        self.arm_raised = True
        self.gripper_closed = False
        self.carrying_object = False
        self.status = "idle"
        self.current_path = []
        self.traveled_path = [(1, 7)]
        self.target_position = None
        self.auto_active = False
        self.phase_ticks_remaining = 0
        self.step_progress = 0.0
        self.joystick_vector = (0.0, 0.0)
        self.effect_label = ""
        self.effect_ticks = 0
