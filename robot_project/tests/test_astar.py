import unittest

from algorithms.astar import AStarPlanner


class TestAStarPlanner(unittest.TestCase):
    def test_astar_finds_path_around_obstacles(self) -> None:
        planner = AStarPlanner()
        blocked = {(1, 0), (1, 1), (1, 2)}
        path = planner.plan((0, 0), (2, 2), 4, 4, blocked)

        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (2, 2))
        self.assertTrue(all(cell not in blocked for cell in path))

    def test_astar_returns_empty_when_goal_is_unreachable(self) -> None:
        planner = AStarPlanner()
        blocked = {(1, 0), (1, 1), (1, 2), (0, 1), (2, 1)}
        path = planner.plan((0, 0), (2, 2), 3, 3, blocked)

        self.assertEqual(path, [])


if __name__ == "__main__":
    unittest.main()
