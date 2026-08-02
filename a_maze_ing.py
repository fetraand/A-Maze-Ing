"""Main entry point for the A-Maze-ing program."""

import random
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import animation
import color
import mazegen
import parsing
import to_maze_txt


def _regeneration_seed(config_data: Dict[str, Any]) -> Optional[int]:
    """Determine the seed to use for regeneration.

    If a fixed seed (SEED) is defined in the configuration, it is always
    reused so that the maze remains identical across regenerations and
    program restarts. If no seed is defined, a new random seed is drawn on
    each call.

    Args:
        config_data: The current configuration dictionary.

    Returns:
        Optional[int]: The seed to use for generation.
    """
    fixed_seed: Optional[int] = config_data.get("seed")
    if fixed_seed is not None:
        return fixed_seed
    return random.randint(1, 99999)


def interactive_key(
    my_maze: mazegen.Maze,
    config_data: Dict[str, Any],
    output_filename: str
) -> None:
    """Handle user interactions (colors, regeneration, size).

    Args:
        my_maze: The current maze instance.
        config_data: Configuration parameter dictionary.
        output_filename: Output file for saving data.
    """
    show_path: bool = True

    current_maze_color: str = color.MAZE_RED
    current_c42_color: str = color.C42_DEEP
    current_path_color: str = color.PATH_YELLOW
    current_bg_color: str = color.BG_BLACK

    while True:
        sys.stdout.flush()

        solved_path: List[Tuple[int, int]] = mazegen.solve(my_maze)
        path: List[Tuple[int, int]] = solved_path if show_path else []

        to_maze_txt.save_maze_data(
            output_filename, my_maze, solved_path
        )

        print(f"\n{color.MAZE_AMBER}=== A - MAZE - ING ==={color.RESET}")
        color.display_colored_maze(
            maze=my_maze,
            path=path,
            maze_color=current_maze_color,
            c42_color=current_c42_color,
            path_color=current_path_color,
            bg_color=current_bg_color
        )

        print(f"\n{color.MAZE_AMBER}===[SWITCH LIST]==={color.RESET}")
        print(f"{color.MAZE_GREEN}r : REGENERATE LABYRINTH{color.RESET}")
        print(f"{color.MAZE_GREEN}t : CHANGE MAZE SIZE{color.RESET}")
        print(
            f"{color.MAZE_GREEN}h : SEE/NOT THE PATH "
            f"(ANIMATION){color.RESET}"
        )
        print(f"{color.MAZE_GREEN}g : ACTIVATE GAMER MODE{color.RESET}")
        print(f"{color.MAZE_GREEN}e : CHANGE ENTRY COORD{color.RESET}")
        print(f"{color.MAZE_GREEN}o : CHANGE EXIT COORD{color.RESET}")
        print(f"{color.MAZE_GREEN}2 : CHANGE MAZE COLOR{color.RESET}")
        print(f"{color.MAZE_GREEN}4 : CHANGE PATTERN COLOR{color.RESET}")
        print(f"{color.MAZE_GREEN}6 : CHANGE FONT COLOR{color.RESET}")
        print(f"{color.MAZE_GREEN}q : QUIT PROGRAM{color.RESET}")

        prompt: str = f"\n{color.MAZE_AMBER}YOUR CHOICE : {color.RESET}"

        try:
            choice: str = input(prompt).strip().lower()
            animation.flush_input()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            animation.anim_quit()
            return

        if choice == "q":
            animation.anim_quit()
            break
        elif choice == "h":
            show_path = not show_path
            if show_path:
                actual_path: List[Tuple[int, int]] = mazegen.solve(my_maze)
                animation.anim_path(my_maze, actual_path)
        elif choice == "g":
            animation.gamer_mode(my_maze)
        elif choice == "r":
            print(f"{color.MAZE_AMBER}Regenerate maze...{color.RESET}")
            try:
                candidate: mazegen.Maze = mazegen.Maze(
                    width=config_data["width"],
                    height=config_data["height"],
                    seed=_regeneration_seed(config_data),
                    perfect=config_data["perfect"]
                )
                candidate.entry = config_data["entry"]
                candidate.exit = config_data["exit"]
                candidate.gen_dfs(
                    start_x=candidate.entry[0], start_y=candidate.entry[1]
                )
                my_maze = candidate
            except (TypeError, ValueError, IndexError) as err:
                print(
                    f"{color.MAZE_RED}Regeneration failed : "
                    f"{err}{color.RESET}"
                )
                time.sleep(1.5)
        elif choice == "t":
            try:
                msg_sz: str = (
                    f"{color.MAZE_AMBER}New size "
                    f"(width,height) : {color.RESET}"
                )
                new_size_str: str = input(msg_sz)
                parts: List[str] = [
                    p.strip() for p in new_size_str.split(",") if p.strip()
                ]
                if len(parts) != 2:
                    raise ValueError(
                        "Size requires exactly two numbers (width,height)."
                    )

                new_w: int = int(parts[0])
                new_h: int = int(parts[1])

                if new_w < 11 or new_h < 9:
                    raise ValueError("Dimensions must be at least 11x9.")
                if new_w > 50 or new_h > 45:
                    raise ValueError("Max width is 50 and max height is 45.")

                old_entry: Tuple[int, int] = config_data["entry"]
                old_exit: Tuple[int, int] = config_data["exit"]
                entry_still_valid: bool = (
                    0 <= old_entry[0] < new_w
                    and 0 <= old_entry[1] < new_h
                )
                exit_still_valid: bool = (
                    0 <= old_exit[0] < new_w
                    and 0 <= old_exit[1] < new_h
                )

                if (
                    entry_still_valid
                    and exit_still_valid
                    and old_entry != old_exit
                ):
                    config_data["entry"] = old_entry
                    config_data["exit"] = old_exit
                else:
                    config_data["entry"] = (0, 0)
                    config_data["exit"] = (new_w - 1, new_h - 1)

                config_data["width"] = new_w
                config_data["height"] = new_h

                print(
                    f"{color.MAZE_GREEN}Size updated! "
                    f"Regenerating...{color.RESET}"
                )

                candidate = mazegen.Maze(
                    width=config_data["width"],
                    height=config_data["height"],
                    seed=_regeneration_seed(config_data),
                    perfect=config_data["perfect"]
                )
                candidate.entry = config_data["entry"]
                candidate.exit = config_data["exit"]
                candidate.gen_dfs(
                    start_x=candidate.entry[0], start_y=candidate.entry[1]
                )
                my_maze = candidate
                time.sleep(1)
            except (KeyboardInterrupt, EOFError):
                print(f"\n{color.MAZE_RED}Operation cancelled.{color.RESET}")
                time.sleep(1)
            except (ValueError, IndexError) as err:
                print(
                    f"{color.MAZE_RED}Invalid size format : "
                    f"{err}{color.RESET}"
                )
                time.sleep(1.5)
        elif choice == "2":
            colors_list: List[str] = [
                color.MAZE_RED, color.MAZE_GREEN, color.MAZE_AMBER
            ]
            idx: int = (
                colors_list.index(current_maze_color) + 1
            ) % len(colors_list)
            current_maze_color = colors_list[idx]
        elif choice == "4":
            c42_list: List[str] = [
                color.C42_DEEP, color.C42_CYAN, color.C42_LIGHT
            ]
            idx = (c42_list.index(current_c42_color) + 1) % len(c42_list)
            current_c42_color = c42_list[idx]
        elif choice == "6":
            bg_list: List[str] = [
                color.BG_BLACK, color.BG_GREY, color.BG_BLUE
            ]
            idx = (bg_list.index(current_bg_color) + 1) % len(bg_list)
            current_bg_color = bg_list[idx]
        elif choice == "e":
            try:
                msg_ent: str = (
                    f"{color.MAZE_AMBER}Entry coordinates "
                    f"(format x,y) : {color.RESET}"
                )
                new_entry_str: str = input(msg_ent)
                parts = [
                    p.strip() for p in new_entry_str.split(",") if p.strip()
                ]
                if len(parts) != 2:
                    raise ValueError("Insert exactly two numbers (x, y)")

                new_entry: Tuple[int, int] = (int(parts[0]), int(parts[1]))
                if not (
                    0 <= new_entry[0] < my_maze.width
                    and 0 <= new_entry[1] < my_maze.height
                ):
                    raise IndexError("Outside coordinates")
                if new_entry == my_maze.exit:
                    raise ValueError("The input cannot be on the output")

                prev_entry: Tuple[int, int] = my_maze.entry
                my_maze.entry = new_entry
                try:
                    mazegen.solve(my_maze)
                except RuntimeError as solve_err:
                    my_maze.entry = prev_entry
                    raise ValueError(
                        "This entry makes the maze unsolvable "
                        f"(it may be inside the '42' pattern) : "
                        f"{solve_err}"
                    ) from solve_err

                config_data["entry"] = new_entry
                print(
                    f"{color.MAZE_GREEN}New entry defined in "
                    f"{new_entry} !{color.RESET}"
                )
                time.sleep(1)
            except (KeyboardInterrupt, EOFError):
                print(f"\n{color.MAZE_RED}Operation cancelled.{color.RESET}")
                time.sleep(1)
            except (ValueError, IndexError) as err:
                print(f"{color.MAZE_RED}Invalid entry : {err}{color.RESET}")
                time.sleep(1.5)
        elif choice == "o":
            try:
                msg_ex: str = (
                    f"{color.MAZE_AMBER}Exit coordinates "
                    f"(format x,y) : {color.RESET}"
                )
                new_exit_str: str = input(msg_ex)
                parts = [
                    p.strip() for p in new_exit_str.split(",") if p.strip()
                ]
                if len(parts) != 2:
                    raise ValueError("Insert exactly two numbers (x, y)")

                new_exit: Tuple[int, int] = (int(parts[0]), int(parts[1]))
                if not (
                    0 <= new_exit[0] < my_maze.width
                    and 0 <= new_exit[1] < my_maze.height
                ):
                    raise IndexError("Outside coordinates")
                if new_exit == my_maze.entry:
                    raise ValueError("The input cannot be on the output")

                prev_exit: Tuple[int, int] = my_maze.exit
                my_maze.exit = new_exit
                try:
                    mazegen.solve(my_maze)
                except RuntimeError as solve_err:
                    my_maze.exit = prev_exit
                    raise ValueError(
                        "This exit makes the maze unsolvable "
                        f"(it may be inside the '42' pattern) : "
                        f"{solve_err}"
                    ) from solve_err

                config_data["exit"] = new_exit
                print(
                    f"{color.MAZE_GREEN}New exit defined in "
                    f"{new_exit} !{color.RESET}"
                )
                time.sleep(1)
            except (KeyboardInterrupt, EOFError):
                print(f"\n{color.MAZE_RED}Operation cancelled.{color.RESET}")
                time.sleep(1)
            except (ValueError, IndexError) as err:
                print(f"{color.MAZE_RED}Invalid exit : {err}{color.RESET}")
                time.sleep(1.5)
        else:
            print(
                f"{color.MAZE_RED}OPTION INVALID, "
                f"PLEASE TRY AGAIN{color.RESET}"
            )
            time.sleep(1)


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            print(
                "Usage: python3 a_maze_ing.py <config_file>",
                file=sys.stderr
            )
            sys.exit(1)

        config_path: str = sys.argv[1]
        config_data: Dict[str, Any] = parsing.parse_config(config_path)
        output_filename: str = str(config_data["output_file"])

        my_maze: mazegen.Maze = mazegen.Maze(
            width=config_data["width"],
            height=config_data["height"],
            seed=config_data["seed"],
            perfect=config_data["perfect"]
        )

        my_maze.entry = config_data["entry"]
        my_maze.exit = config_data["exit"]

        my_maze.gen_dfs(
            start_x=my_maze.entry[0], start_y=my_maze.entry[1]
        )

        animation.anim_launch()
        interactive_key(my_maze, config_data, output_filename)

    except (KeyboardInterrupt, EOFError):
        print("\n")
        animation.anim_quit()
        sys.exit(0)
    except (TypeError, ValueError, RuntimeError, IndexError, OSError) as e:
        error_msg = f"ERROR: {e}"
        print(error_msg, file=sys.stderr)
        if "config_data" in locals():
            try:
                to_maze_txt.save_error_data(
                    str(config_data["output_file"]), error_msg
                )
            except Exception as file_err:
                print(
                    f"Unable to write error to file: {file_err}",
                    file=sys.stderr
                )
        sys.exit(1)
