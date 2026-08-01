"""ANSI color handling and maze display in the terminal."""

from typing import Any, List, Set, Tuple

RESET: str = "\033[0m"

MAZE_AMBER: str = "\033[33m"
MAZE_GREEN: str = "\033[32m"
MAZE_RED: str = "\033[31m"

BG_BLACK: str = "\033[40m"
BG_GREY: str = "\033[100m"
BG_BLUE: str = "\033[44m"

C42_DEEP: str = "\033[34m"
C42_CYAN: str = "\033[36m"
C42_LIGHT: str = "\033[96m"

PATH_YELLOW: str = "\033[93m"


def colorize(text: str, color_code: str) -> str:
    """Wrap text with an ANSI color code and apply a RESET.

    Args:
        text: The raw text to color.
        color_code: The ANSI color code string.

    Returns:
        The formatted text with color and reset applied.
    """
    return f"{color_code}{text}{RESET}"


def display_colored_maze(
    maze: Any,
    path: List[Tuple[int, int]],
    maze_color: str,
    c42_color: str,
    path_color: str,
    bg_color: str = ""
) -> None:
    """Display the maze in the terminal with the selected styles.

    Args:
        maze: The generated Maze object instance.
        path: List of coordinates for the shortest path.
        maze_color: ANSI color code for the maze walls.
        c42_color: ANSI color code for the 42-pattern block.
        path_color: ANSI color code for the solution path.
        bg_color: Optional ANSI color code for the background.
    """
    path_set: Set[Tuple[int, int]] = set(path) if path else set()

    corner: str = colorize("☲", bg_color + maze_color)
    horiz_wall: str = colorize("☵☵☵", bg_color + maze_color)
    vert_wall: str = colorize("☲", bg_color + maze_color)

    pattern_42_bloc: str = colorize("███", bg_color + c42_color)
    path_char: str = colorize(" * ", bg_color + path_color)

    empty_char: str = colorize("   ", bg_color)
    horiz_empty: str = colorize("   ", bg_color)
    vert_empty: str = colorize(" ", bg_color)
    chick: str = colorize(" 🐥", bg_color)
    ver: str = colorize(" 🐛", bg_color)

    print(corner + (horiz_wall + corner) * int(maze.width))

    for y in range(int(maze.height)):
        row_str: str = vert_wall
        bottom_str: str = corner
        for x in range(int(maze.width)):
            val: int = int(maze.grid[y][x])

            if (x, y) == maze.entry:
                row_str += chick
            elif (x, y) == maze.exit:
                row_str += ver
            elif (x, y) in path_set:
                row_str += path_char
            elif val == 15:
                row_str += pattern_42_bloc
            else:
                row_str += empty_char

            if bool(val & int(maze.LINE_E)):
                row_str += vert_wall
            else:
                row_str += vert_empty

            if bool(val & int(maze.LINE_S)):
                bottom_str += horiz_wall
            else:
                bottom_str += horiz_empty
            bottom_str += corner

        print(row_str)
        print(bottom_str)
