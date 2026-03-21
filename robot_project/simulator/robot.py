from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

GridPoint = Tuple[int, int]


@dataclass
class RobotState:
    position: GridPoint = (1, 7)
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
        self.current_path = path[1:] if len(path) > 1 else []
        self.target_position = target
        self.step_progress = 0.0

    def record_position(self) -> None:
        if not self.traveled_path or self.traveled_path[-1] != self.position:
            self.traveled_path.append(self.position)

    def manual_move(self, destination: GridPoint) -> None:
        self.position = destination
        self.record_position()
