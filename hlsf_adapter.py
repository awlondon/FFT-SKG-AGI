import numpy as np
from functools import lru_cache
from typing import Tuple, List


def multiplier(level: int, sides: int) -> float:
    """Scaling multiplier used for nested symmetry calculations."""
    if sides % 2 == 0:
        return 2 ** (level - 2)
    else:
        return 1.5 ** (level - 2)


@lru_cache(maxsize=None)
def _generate_vertices_impl(center: Tuple[float, float], radius: float, sides: int) -> List[Tuple[float, float]]:
    angles = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    x = center[0] + radius * np.sin(angles)
    y = center[1] + radius * np.cos(angles)
    return list(zip(x, y))


def generate_vertices(center: Tuple[float, float], radius: float, sides: int) -> List[Tuple[float, float]]:
    if isinstance(center, np.ndarray):
        center = tuple(center.tolist())
    return _generate_vertices_impl(center, radius, sides)


def midpoint(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def calculate_symmetry_point_adjusted(center: Tuple[float, float], radius: float, sides: int, level: int) -> np.ndarray:
    center2d = np.array(center, dtype=float)
    if level <= 1:
        return center2d

    cumulative_offset = np.array([0.0, 0.0])
    for current_level in range(2, level + 1):
        scaling_factor = multiplier(current_level, sides)
        current_adjustment = radius * scaling_factor
        verts = generate_vertices(center2d, current_adjustment, sides)
        if sides % 2 == 1:
            current_offset = np.array(midpoint(verts[0], verts[1])) - center2d
        else:
            current_offset = np.array(verts[0]) - center2d
        cumulative_offset += current_offset
    return center2d + cumulative_offset
