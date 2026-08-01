"""Reusable package for maze generation and solving.

This package exposes the :class:`Maze` class to generate a maze and
the :func:`solve` function to calculate the shortest path between its
entrance and exit. See README_MAZEGEN.md for complete usage documentation.
"""

from .maze_gen import Maze
from .solver import solve

__all__ = ["Maze", "solve"]
