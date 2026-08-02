"""Read and validate the maze configuration file."""

from typing import Any, Dict, Set, Tuple

VALID_KEYS: Set[str] = {
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
    "SEED",
}


def _parse_coord(coord_str: str, coord_type: str) -> Tuple[int, int]:
    """Parse and validate a coordinate string in x,y format.

    Args:
        coord_str: The coordinate string (e.g. '1,3').
        coord_type: The coordinate option name ('ENTRY' or 'EXIT').

    Returns:
        Tuple[int, int]: The cleaned coordinates as a tuple.

    Raises:
        ValueError: If the format or numeric values are invalid.
    """
    parts = [p.strip() for p in coord_str.split(",") if p.strip()]
    if len(parts) != 2:
        raise ValueError(
            f"Invalid format for {coord_type}: expected exactly 2 numbers "
            f"separated by a comma (e.g., '1,3'), got '{coord_str}'"
        )
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        raise ValueError(
            f"Invalid numbers in {coord_type} coordinates: '{coord_str}'"
        )


def parse_config(filename: str) -> Dict[str, Any]:
    """Parse the configuration file and strictly validate the options.

    Args:
        filename: The path to the configuration file.

    Returns:
        Dict[str, Any]: A dictionary containing the validated options.

    Raises:
        ValueError: If the file is corrupted or contains out-of-bounds data.
    """
    try:
        with open(filename, "r") as f:
            cfg: Dict[str, str] = {}
            for line_number, raw_line in enumerate(f, start=1):
                no_comment: str = raw_line.split("#", 1)[0].strip()
                if not no_comment:
                    continue
                if "=" not in no_comment:
                    raise ValueError(
                        f"Invalid line {line_number} in config file "
                        f"(expected 'KEY=VALUE'): '{no_comment}'"
                    )
                key, value = no_comment.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key in cfg:
                    raise ValueError(
                        f"Duplicate key '{key}' found in config file."
                    )
                cfg[key] = value

        unknown_keys = sorted(set(cfg) - VALID_KEYS)
        if unknown_keys:
            raise ValueError(
                f"Unknown key(s) in config file: {', '.join(unknown_keys)}. "
                f"Allowed keys: {', '.join(sorted(VALID_KEYS))}"
            )

        if "WIDTH" not in cfg or "HEIGHT" not in cfg:
            raise ValueError("WIDTH and HEIGHT must be defined in config.")

        width = int(cfg["WIDTH"])
        height = int(cfg["HEIGHT"])

        if width < 11 or height < 9:
            raise ValueError(
                f"Maze dimensions too small: ({width}x{height}). "
                "Minimum size is 11x9."
            )
        if width > 50 or height > 45:
            raise ValueError(
                f"Maze dimensions out of bounds: ({width}x{height}). "
                "Maximum allowed is width 50 and height 45."
            )

        if "ENTRY" not in cfg or "EXIT" not in cfg:
            raise ValueError("ENTRY and EXIT must be defined in config.")

        entry = _parse_coord(cfg["ENTRY"], "ENTRY")
        exit_coord = _parse_coord(cfg["EXIT"], "EXIT")

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError(
                f"ENTRY coordinates {entry} are out of maze bounds "
                f"({width}x{height})."
            )
        if not (0 <= exit_coord[0] < width and 0 <= exit_coord[1] < height):
            raise ValueError(
                f"EXIT coordinates {exit_coord} are out of maze bounds "
                f"({width}x{height})."
            )

        if entry == exit_coord:
            raise ValueError(
                f"ENTRY {entry} and EXIT {exit_coord} must be different."
            )

        raw_seed = cfg.get("SEED", "None").strip()
        if raw_seed.lower() in ("none", ""):
            seed_value = None
        else:
            seed_value = int(raw_seed)
            if seed_value < 0:
                raise ValueError(
                    f"SEED must be a positive integer, got '{raw_seed}'. "
                    "Python ignores the sign of an integer seed, so a "
                    "negative value would produce the same maze as its "
                    "absolute value."
                )

        if "PERFECT" not in cfg:
            raise ValueError("PERFECT must be defined in config.")

        raw_perfect = cfg["PERFECT"].strip().lower()
        if raw_perfect in ("true", "1", "yes"):
            perfect_value = True
        elif raw_perfect in ("false", "0", "no"):
            perfect_value = False
        else:
            raise ValueError(
                f"Invalid value for PERFECT: '{cfg.get('PERFECT')}'. "
                "Expected 'True' or 'False'."
            )

        if "OUTPUT_FILE" not in cfg or not cfg["OUTPUT_FILE"]:
            raise ValueError("OUTPUT_FILE must be defined in config.")

        return {
            "width": width,
            "height": height,
            "entry": entry,
            "exit": exit_coord,
            "seed": seed_value,
            "output_file": cfg["OUTPUT_FILE"],
            "perfect": perfect_value
        }
    except Exception as e:
        raise ValueError(
            f"Critical ERROR of configuration ({filename}) : {e}"
        ) from e
