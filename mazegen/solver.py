"""Maze solving using breadth-first search (BFS)."""

from typing import List, Tuple

from .maze_gen import Maze


def solve(maze: Maze) -> List[Tuple[int, int]]:
    """Solve the maze using a breadth-first search algorithm.

    Args:
        maze: The generated maze instance containing the grid and the
            entry/exit access points.

    Returns:
        List[Tuple[int, int]]: The list of coordinates (x, y) for the path.

    Raises:
        RuntimeError: If the maze is not generated or is unsolvable.
    """
    if not bool(maze.is_generated):
        raise RuntimeError(
            "Cannot solve a maze that hasn't been generated yet"
        )

    line_n: int = 1
    line_e: int = 2
    line_s: int = 4
    line_w: int = 8

    start: Tuple[int, int] = (int(maze.entry[0]), int(maze.entry[1]))
    target: Tuple[int, int] = (int(maze.exit[0]), int(maze.exit[1]))

    maze_w: int = int(maze.width)
    maze_h: int = int(maze.height)

    waiting_list: List[Tuple[Tuple[int, int], List[Tuple[int, int]]]] = [
        (start, [start])
    ]
    visited: List[List[bool]] = [
        [False for _ in range(maze_w)]
        for _ in range(maze_h)
    ]
    visited[start[1]][start[0]] = True

    while waiting_list:
        (cx, cy), path = waiting_list.pop(0)

        if (cx, cy) == target:
            return path

        val: int = int(maze.grid[cy][cx])

        if not bool(val & line_n) and cy > 0 and not visited[cy - 1][cx]:
            visited[cy - 1][cx] = True
            waiting_list.append(((cx, cy - 1), path + [(cx, cy - 1)]))

        if (
            not bool(val & line_e)
            and cx < maze_w - 1
            and not visited[cy][cx + 1]
        ):
            visited[cy][cx + 1] = True
            waiting_list.append(((cx + 1, cy), path + [(cx + 1, cy)]))

        if (
            not bool(val & line_s)
            and cy < maze_h - 1
            and not visited[cy + 1][cx]
        ):
            visited[cy + 1][cx] = True
            waiting_list.append(((cx, cy + 1), path + [(cx, cy + 1)]))

        if not bool(val & line_w) and cx > 0 and not visited[cy][cx - 1]:
            visited[cy][cx - 1] = True
            waiting_list.append(((cx - 1, cy), path + [(cx - 1, cy)]))

    raise RuntimeError(
        "Unsolvable maze: No path found between entry and exit."
    )
