from __future__ import annotations

from heapq import heappop, heappush
from typing import Dict, Iterable, List, Optional, Protocol, Sequence, Set, Tuple

GridPoint = Tuple[int, int]


class PathPlanner(Protocol):
    def plan(
        self,
        start: GridPoint,
        goal: GridPoint,
        width: int,
        height: int,
        blocked: Set[GridPoint],
    ) -> List[GridPoint]:
        """Return a path from start to goal on a grid."""


class AStarPlanner:
    """A simple 4-connected A* planner for grid worlds."""

    def __init__(self, allow_diagonal: bool = False) -> None:
        self.allow_diagonal = allow_diagonal

    def plan(
        self,
        start: GridPoint,
        goal: GridPoint,
        width: int,
        height: int,
        blocked: Set[GridPoint],
    ) -> List[GridPoint]:
        if not self._within_bounds(start, width, height) or not self._within_bounds(goal, width, height):
            return []
        if start == goal:
            return [start]

        frontier: List[Tuple[float, GridPoint]] = []
        heappush(frontier, (0.0, start))
        came_from: Dict[GridPoint, Optional[GridPoint]] = {start: None}
        cost_so_far: Dict[GridPoint, float] = {start: 0.0}

        while frontier:
            _, current = heappop(frontier)
            if current == goal:
                return self._reconstruct_path(came_from, goal)

            for neighbor in self._neighbors(current, width, height):
                if neighbor in blocked and neighbor != goal:
                    continue

                new_cost = cost_so_far[current] + 1.0
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self._heuristic(goal, neighbor)
                    heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current

        return []

    def _neighbors(self, point: GridPoint, width: int, height: int) -> Iterable[GridPoint]:
        x, y = point
        directions: Sequence[GridPoint]
        if self.allow_diagonal:
            directions = (
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
                (1, 1),
                (-1, -1),
                (-1, 1),
                (1, -1),
            )
        else:
            directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

        for dx, dy in directions:
            neighbor = (x + dx, y + dy)
            if self._within_bounds(neighbor, width, height):
                yield neighbor

    @staticmethod
    def _heuristic(goal: GridPoint, point: GridPoint) -> int:
        return abs(goal[0] - point[0]) + abs(goal[1] - point[1])

    @staticmethod
    def _within_bounds(point: GridPoint, width: int, height: int) -> bool:
        x, y = point
        return 0 <= x < width and 0 <= y < height

    @staticmethod
    def _reconstruct_path(came_from: Dict[GridPoint, Optional[GridPoint]], goal: GridPoint) -> List[GridPoint]:
        current = goal
        path = [current]
        while came_from[current] is not None:
            current = came_from[current]  # type: ignore[assignment]
            path.append(current)
        path.reverse()
        return path
