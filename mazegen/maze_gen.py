"""Generation and representation of a perfect or imperfect maze."""

from __future__ import annotations
from typing import List, Optional, Set, Tuple
import random


class Maze:
    """Represents the complete maze structure and its generation.

    Attributes:
        LINE_N (int): Binary mask for the north wall (1).
        LINE_E (int): Binary mask for the east wall (2).
        LINE_S (int): Binary mask for the south wall (4).
        LINE_W (int): Binary mask for the west wall (8).
        width (int): Maze width in number of cells.
        height (int): Maze height in number of cells.
        perfect (bool): Indicates whether the maze has a unique path.
        is_generated (bool): Generation state of the maze.
        grid (List[List[int]]): Matrix of integers describing the wall state.
        entry (Tuple[int, int]): Coordinates (x, y) of the entry point.
        exit (Tuple[int, int]): Coordinates (x, y) of the exit point.
    """

    LINE_N: int = 1
    LINE_E: int = 2
    LINE_S: int = 4
    LINE_W: int = 8

    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int] = None,
        perfect: bool = True
    ) -> None:
        """Initialize the maze grid and apply the random seed.

        Args:
            width: Maze width in number of cells.
            height: Maze height in number of cells.
            seed: Optional seed for reproducibility.
            perfect: Determines whether the maze is perfect (without loops).

        Raises:
            TypeError: If width, height, or seed are not of the correct type.
            ValueError: If the dimensions are negative or outside the allowed
            constraints.
        """
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError("width and height must be integers")
        if width <= 0 or height <= 0:
            raise ValueError("Please insert positive values")
        if seed is not None and not isinstance(seed, int):
            raise TypeError("seed must be an integer or None")

        self.width: int = width
        self.height: int = height
        self.perfect: bool = perfect
        self.is_generated: bool = False
        self._rng: random.Random = random.Random(seed)

        self.grid: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)
        ]
        self.entry: Tuple[int, int] = (0, 0)
        if self.entry[0] >= self.width or self.entry[1] >= self.height:
            raise ValueError("ERROR: entry invalid")

        self.exit: Tuple[int, int] = (width - 1, height - 1)
        if (
            self.exit[0] > (self.width - 1)
            or self.exit[1] > (self.height - 1)
        ):
            raise ValueError("ERROR: output invalid")

        if self.entry == self.exit:
            raise ValueError(
                "ERROR: entry and exit should not be in the same location"
            )

    def break_wall(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Break the separating wall between two adjacent cells.

        Args:
            x1: X coordinate of the first cell.
            y1: Y coordinate of the first cell.
            x2: X coordinate of the second cell.
            y2: Y coordinate of the second cell.
        """
        if x1 < x2:
            self.grid[y1][x1] &= ~self.LINE_E
            self.grid[y2][x2] &= ~self.LINE_W
        elif x1 > x2:
            self.grid[y1][x1] &= ~self.LINE_W
            self.grid[y2][x2] &= ~self.LINE_E
        elif y1 < y2:
            self.grid[y1][x1] &= ~self.LINE_S
            self.grid[y2][x2] &= ~self.LINE_N
        elif y1 > y2:
            self.grid[y1][x1] &= ~self.LINE_N
            self.grid[y2][x2] &= ~self.LINE_S

    def _42_pattern(self, visited: List[List[bool]]) -> bool:
        """Draw the '42' pattern made of fully closed cells.

        Args:
            visited: Matrix tracking the cells already explored.

        Returns:
            bool: True when the pattern is applied correctly.

        Raises:
            ValueError: If the maze size is too small to fit the '42' pattern.
        """
        pattern: List[List[int]] = [
            [1, 0, 1, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1]
        ]
        p_h: int = len(pattern)
        p_w: int = len(pattern[0])

        if self.width < p_w + 4 or self.height < p_h + 4:
            raise ValueError(
                "ERROR: Maze too small to embed the '42' pattern"
            )

        start_x: int = (self.width - p_w) // 2
        start_y: int = (self.height - p_h) // 2

        for py in range(p_h):
            for px in range(p_w):
                if pattern[py][px] == 1:
                    gx: int = start_x + px
                    gy: int = start_y + py
                    self.grid[gy][gx] = 15
                    visited[gy][gx] = True
        return True

    def _window_is_fully_open(self, win_x: int, win_y: int) -> bool:
        """Check whether the 3x3 window at (win_x, win_y) is open.

        Args:
            win_x: X coordinate of the top-left corner of the 3x3 window.
            win_y: Y coordinate of the top-left corner of the 3x3 window.

        Returns:
            bool: True if all 12 internal walls of this 3x3 window are open
                (a free-flow area forbidden by the challenge).
        """
        horizontally_open = all(
            self.grid[yy][xx] & self.LINE_E == 0
            for yy in range(win_y, win_y + 3)
            for xx in range(win_x, win_x + 2)
        )
        if not horizontally_open:
            return False
        return all(
            self.grid[yy][xx] & self.LINE_S == 0
            for yy in range(win_y, win_y + 2)
            for xx in range(win_x, win_x + 3)
        )

    def _open_area_near(self, x: int, y: int) -> bool:
        """Detect an open 3x3 area in the immediate vicinity of (x, y).

        It scans only the few 3x3 windows that could contain the given cell,
        to stay efficient when adding loops to large mazes.

        Args:
            x: X coordinate of the cell whose wall has just been broken.
            y: Y coordinate of the cell whose wall has just been broken.

        Returns:
            bool: True if an open 3x3-cell area (or larger) appears around
                this cell.
        """
        if self.width < 3 or self.height < 3:
            return False
        for win_y in range(max(0, y - 2), min(y, self.height - 3) + 1):
            for win_x in range(max(0, x - 2), min(x, self.width - 3) + 1):
                if self._window_is_fully_open(win_x, win_y):
                    return True
        return False

    def _has_open_3x3_area(self) -> bool:
        """Scan the whole grid for an open 3x3 area.

        This acts as a final safety net, independent of the generation method,
        ensuring that no fully open 3x3-cell area (or larger)
        could have formed.

        Returns:
            bool: True if such an area exists somewhere on the grid.
        """
        if self.width < 3 or self.height < 3:
            return False
        return any(
            self._window_is_fully_open(x, y)
            for y in range(self.height - 2)
            for x in range(self.width - 2)
        )

    def gen_dfs(self, start_x: int = 0, start_y: int = 0) -> None:
        """Generate the maze using an iterative depth-first traversal.

        Args:
            start_x: X coordinate of the generation start.
            start_y: Y coordinate of the generation start.

        Raises:
            IndexError: If the start point lies outside the maze bounds.
            ValueError: If the maze is too small for the '42' pattern, or if
                the start/end point collides with the '42' pattern.
            RuntimeError: If, despite the safeguards, a fully open 3x3-cell
                area (or larger) is detected in the generated maze (a
                defensive guard, which should normally never happen).
        """
        if (
            start_x < 0
            or start_x >= self.width
            or start_y < 0
            or start_y >= self.height
        ):
            raise IndexError(
                "Start coordinates are outside the maze boundaries"
            )

        visited: List[List[bool]] = [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]

        self._42_pattern(visited)

        if visited[start_y][start_x]:
            raise ValueError(
                f"({start_x}, {start_y}) are in the box strictly "
                "reserved for pattern 42, please change the values"
            )

        ex, ey = self.exit
        if visited[ey][ex]:
            raise ValueError(
                f"ERROR: The exit point ({ey}, {ex}) is located "
                "inside the '42' pattern. It is strictly forbidden "
                "to break the walls of the 42 motif."
            )

        stack: List[Tuple[int, int]] = [(start_x, start_y)]
        visited[start_y][start_x] = True

        while stack:
            cx, cy = stack[-1]
            neighbors: List[Tuple[int, int]] = []

            if cy > 0 and not visited[cy - 1][cx]:
                neighbors.append((cx, cy - 1))
            if cx < self.width - 1 and not visited[cy][cx + 1]:
                neighbors.append((cx + 1, cy))
            if cy < self.height - 1 and not visited[cy + 1][cx]:
                neighbors.append((cx, cy + 1))
            if cx > 0 and not visited[cy][cx - 1]:
                neighbors.append((cx - 1, cy))

            if neighbors:
                nx, ny = self._rng.choice(neighbors)
                self.break_wall(cx, cy, nx, ny)
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

        if not self.perfect:
            loops_to_create: int = (self.width * self.height) // 10
            attempts: int = 0
            while loops_to_create > 0 and attempts < 2000:
                attempts += 1
                rx = self._rng.randint(1, self.width - 2)
                ry = self._rng.randint(1, self.height - 2)

                if self.grid[ry][rx] != 15 and self.grid[ry][rx + 1] != 15:
                    if self.grid[ry][rx] & self.LINE_E:
                        self.break_wall(rx, ry, rx + 1, ry)
                        if self._open_area_near(rx, ry):
                            self.grid[ry][rx] |= self.LINE_E
                            self.grid[ry][rx + 1] |= self.LINE_W
                        else:
                            loops_to_create -= 1

        if self._has_open_3x3_area():
            raise RuntimeError(
                "Internal error: the generated maze contains a "
                "forbidden 3x3 (or larger) fully open area."
            )

        self.is_generated = True

    def to_hex_string(self) -> str:
        """Convert the grid to a hexadecimal string.

        Returns:
            str: Text representation of the bit values of each cell.

        Raises:
            RuntimeError: If the maze has not been generated yet.
        """
        if not self.is_generated:
            raise RuntimeError(
                "Cannot export a maze that hasn't been generated yet."
            )
        return "\n".join(
            "".join(f"{cell:X}" for cell in row) for row in self.grid
        )

    def display_ascii(
        self,
        path: Optional[List[Tuple[int, int]]] = None
    ) -> None:
        """Display the maze in ASCII format to standard output.

        Args:
            path: List of coordinates representing the path to display.

        Raises:
            RuntimeError: If the maze has not been generated yet.
        """
        if not self.is_generated:
            raise RuntimeError(
                "Cannot display a maze that hasn't been generated yet."
            )

        path_set: Set[Tuple[int, int]] = set(path) if path else set()
        corner: str = "☲"
        horiz: str = "☲☲☲"
        vert: str = "☲"

        print(corner + (horiz + corner) * self.width)
        for y in range(self.height):
            row_str: str = vert
            bottom_str: str = corner
            for x in range(self.width):
                val: int = self.grid[y][x]
                if (x, y) == self.entry:
                    row_str += " 🐥"
                elif (x, y) == self.exit:
                    row_str += "🐛 "
                elif (x, y) in path_set:
                    row_str += " * "
                elif val == 15:
                    row_str += "███"
                else:
                    row_str += "   "
                row_str += vert if (val & self.LINE_E) else " "
                bottom_str += horiz if (val & self.LINE_S) else "   "
                bottom_str += corner
            print(row_str)
            print(bottom_str)
