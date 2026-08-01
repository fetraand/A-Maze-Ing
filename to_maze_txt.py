"""Save the maze and errors in the expected text format."""

from typing import Any, List, Tuple


def save_maze_data(
    filename: str, maze: Any, path: List[Tuple[int, int]]
) -> None:
    """Save the maze using the required strict format.

    Args:
        filename: Destination file path.
        maze: Generated maze instance.
        path: List of coordinates for the solution path.
    """
    with open(filename, "w") as f:
        f.write(str(maze.to_hex_string()) + "\n")
        f.write("\n")
        f.write(f"{int(maze.entry[0])},{int(maze.entry[1])}\n")
        f.write(f"{int(maze.exit[0])},{int(maze.exit[1])}\n")

        directions: List[str] = []
        for i in range(len(path) - 1):
            curr_x, curr_y = path[i]
            next_x, next_y = path[i + 1]
            if next_x > curr_x:
                directions.append("E")
            elif next_x < curr_x:
                directions.append("W")
            elif next_y > curr_y:
                directions.append("S")
            elif next_y < curr_y:
                directions.append("N")

        f.write("".join(directions) + "\n")


def save_error_data(filename: str, error_msg: str) -> None:
    """Save the error message to the specified file.

    Args:
        filename: Destination file path.
        error_msg: Text describing the error that occurred.
    """
    with open(filename, "w") as f:
        f.write(f"Please see your ERROR down\n{error_msg}\n")
