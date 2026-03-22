from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Set, Tuple

GridPoint = Tuple[int, int]


@dataclass
class EnvironmentModel:
    grid_width: int = 14
    grid_height: int = 10
    cell_size: int = 48
    object_position: GridPoint = (10, 2)
    goal_position: GridPoint = (11, 7)
    obstacle_mode: bool = False
    obstacles: Set[GridPoint] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.object_position = (10, 2)
        self.goal_position = (11, 7)
        self.obstacles = self._generate_obstacles()
        self.obstacle_mode = False

    def set_obstacle_mode(self, enabled: bool) -> None:
        self.obstacle_mode = enabled

    def visible_obstacles(self) -> Set[GridPoint]:
        return set(self.obstacles) if self.obstacle_mode else set()

    def blocked_cells(self) -> Set[GridPoint]:
        blocked = self.visible_obstacles()
        blocked.discard(self.object_position)
        blocked.discard(self.goal_position)
        return blocked

    def in_bounds(self, cell: GridPoint) -> bool:
        x, y = cell
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height

    def _generate_obstacles(self) -> Set[GridPoint]:
        blocked = {
            (1, 7),
            (2, 7),
            (1, 6),
            self.object_position,
            self.goal_position,
        }
        available = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if (x, y) not in blocked
        ]
        return set(random.sample(available, k=10))
