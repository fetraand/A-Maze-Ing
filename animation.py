"""Terminal animations and visual interactions for A-Maze-ing."""

import curses
import os
import sys
import time
from typing import Any, List, Set, Tuple

import color


def flush_input() -> None:
    """Clear the standard input buffer to ignore typed keys."""
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:
        pass


def anim_launch() -> None:
    """Display the startup loading animation."""
    try:
        os.system("clear")
        title = "=== INITIALIZING A-MAZE-ING SYSTEM ==="
        for char in title:
            sys.stdout.write(f"{color.MAZE_AMBER}{char}{color.RESET}")
            sys.stdout.flush()
            time.sleep(0.04)
        print("\n")

        for i in range(0, 101, 5):
            bar = "█" * (i // 5) + "-" * (20 - (i // 5))
            sys.stdout.write(
                f"\r{color.MAZE_GREEN}[{bar}] {i}% LOADING MODULES..."
                f"{color.RESET}"
            )
            sys.stdout.flush()
            time.sleep(0.05)

        print(f"\n\n{color.PATH_YELLOW}CORE READY.{color.RESET}")
        flush_input()
        input(
            f"\n{color.MAZE_AMBER}[PRESS ENTER TO CRACK THE MAZE]"
            f"{color.RESET}"
        )
        flush_input()
    except KeyboardInterrupt:
        flush_input()
        print(f"\n{color.MAZE_GREEN}Launch skipped.{color.RESET}")


def anim_quit() -> None:
    """Display the shutdown animation sequence when the program closes."""
    try:
        os.system("clear")
        goodbye = "=== CLOSING MAZE CORE INTERFACE ==="
        for char in goodbye:
            sys.stdout.write(f"{color.MAZE_RED}{char}{color.RESET}")
            sys.stdout.flush()
            time.sleep(0.03)
        print("\n")

        messages = [
            "Saving matrix layout...",
            "Cleaning cache sequences...",
            "Disconnecting from grids...",
            "SHUTDOWN COMPLETE. BYE!"
        ]
        for msg in messages:
            print(f"{color.MAZE_AMBER}>> {msg}{color.RESET}")
            time.sleep(0.4)
        time.sleep(0.2)
        os.system("clear")
    except KeyboardInterrupt:
        os.system("clear")


def _draw_game_maze(stdscr: Any, maze: Any, p_x: int, p_y: int) -> None:
    """Draw the maze grid in the curses game-mode interface.

    Args:
        stdscr: The main curses window object.
        maze: The maze instance containing the grid and dimensions.
        p_x: The player's current X position.
        p_y: The player's current Y position.
    """
    stdscr.clear()
    stdscr.addstr(
        0, 0, "=== GAMER MODE: ARROW KEYS TO MOVE ===", curses.color_pair(1)
    )
    stdscr.addstr(
        1, 0, "Press 'Q' to return to menu.", curses.color_pair(2)
    )

    stdscr.addstr(3, 0, "☲" + "☲☲☲☲" * maze.width, curses.color_pair(1))

    for y in range(maze.height):
        row_idx = 4 + y * 2
        stdscr.addstr(row_idx, 0, "☲", curses.color_pair(1))
        stdscr.addstr(row_idx + 1, 0, "☲", curses.color_pair(1))

        for x in range(maze.width):
            val: int = maze.grid[y][x]
            col_pos = 1 + x * 4

            if x == p_x and y == p_y:
                stdscr.addstr(row_idx, col_pos, "🐥 ")
            elif (x, y) == maze.exit:
                stdscr.addstr(row_idx, col_pos, "🐛 ")
            elif val == 15:
                stdscr.addstr(row_idx, col_pos, "███", curses.color_pair(1))
            else:
                stdscr.addstr(row_idx, col_pos, "   ")

            if val & maze.LINE_E:
                stdscr.addstr(row_idx, col_pos + 3, "☲", curses.color_pair(1))
            else:
                stdscr.addstr(row_idx, col_pos + 3, " ")

            if val & maze.LINE_S:
                stdscr.addstr(
                    row_idx + 1, col_pos, "☲☲☲☲", curses.color_pair(1)
                )
            else:
                stdscr.addstr(
                    row_idx + 1, col_pos, "   ☲", curses.color_pair(1)
                )


def gamer_mode(maze: Any) -> None:
    """Start the interactive game mode.

    Allows the player to move the character manually.

    Args:
        maze: The maze instance to explore.
    """
    def main_game(stdscr: Any) -> None:
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        p_x, p_y = maze.entry

        while True:
            try:
                _draw_game_maze(stdscr, maze, p_x, p_y)
            except curses.error:
                stdscr.clear()
                stdscr.addstr(
                    0, 0,
                    "ERROR: Terminal window too small!",
                    curses.color_pair(1)
                )
                stdscr.addstr(
                    1, 0,
                    "Enlarge terminal and try again.",
                    curses.color_pair(3)
                )
                stdscr.addstr(
                    3, 0,
                    "Press any key to return...",
                    curses.color_pair(2)
                )
                stdscr.refresh()
                try:
                    stdscr.getch()
                except KeyboardInterrupt:
                    pass
                return

            stdscr.refresh()

            if (p_x, p_y) == maze.exit:
                try:
                    stdscr.addstr(
                        4 + maze.height * 2, 0,
                        "YOU WIN! Press any key to return...",
                        curses.color_pair(2)
                    )
                    stdscr.refresh()
                    stdscr.getch()
                except (curses.error, KeyboardInterrupt):
                    pass
                return

            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                return

            val: int = maze.grid[p_y][p_x]

            if key in (ord('q'), ord('Q')):
                return
            elif key == curses.KEY_UP and not (val & maze.LINE_N):
                if p_y > 0:
                    p_y -= 1
            elif key == curses.KEY_DOWN and not (val & maze.LINE_S):
                if p_y < maze.height - 1:
                    p_y += 1
            elif key == curses.KEY_LEFT and not (val & maze.LINE_W):
                if p_x > 0:
                    p_x -= 1
            elif key == curses.KEY_RIGHT and not (val & maze.LINE_E):
                if p_x < maze.width - 1:
                    p_x += 1

    try:
        curses.wrapper(main_game)
    except KeyboardInterrupt:
        pass


def anim_path(maze: Any, path: List[Tuple[int, int]]) -> None:
    """Display a step-by-step animation of the solved path.

    Args:
        maze: The maze instance being displayed.
        path: The list of coordinates forming the solution path.
    """
    if not path:
        return

    try:
        for step in range(len(path)):
            os.system("clear")
            print(
                f"\n{color.MAZE_AMBER}=== VISUAL PATH ANIMATION ==="
                f"{color.RESET}"
            )

            current_trail: Set[Tuple[int, int]] = set(path[:step + 1])

            corner = color.colorize("☲", color.MAZE_RED)
            horiz_w = color.colorize("☲☲☲", color.MAZE_RED)
            vert_w = color.colorize("☲", color.MAZE_RED)

            pattern_42_bloc = color.colorize("███", color.C42_DEEP)
            path_char = color.colorize(" * ", color.PATH_YELLOW)
            empty_char = color.colorize("   ", color.BG_BLACK)
            chick = color.colorize("🐥 ", color.BG_BLACK)
            ver = color.colorize("🐛 ", color.BG_BLACK)

            print(corner + (horiz_w + corner) * maze.width)

            for y in range(maze.height):
                row_str = vert_w
                bottom_str = corner
                for x in range(maze.width):
                    val: int = maze.grid[y][x]

                    if (x, y) == path[step]:
                        row_str += chick
                    elif (x, y) == maze.exit:
                        row_str += ver
                    elif (x, y) in current_trail:
                        row_str += path_char
                    elif val == 15:
                        row_str += pattern_42_bloc
                    else:
                        row_str += empty_char

                    if val & maze.LINE_E:
                        row_str += vert_w
                    else:
                        row_str += " "

                    if val & maze.LINE_S:
                        bottom_str += horiz_w
                    else:
                        bottom_str += "   "
                    bottom_str += corner

                print(row_str)
                print(bottom_str)

            time.sleep(0.15)
        time.sleep(0.8)
    except KeyboardInterrupt:
        print(f"\n{color.MAZE_RED}Animation skipped!{color.RESET}")
        time.sleep(0.5)
    finally:
        flush_input()
