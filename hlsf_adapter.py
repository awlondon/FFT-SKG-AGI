from typing import List, Tuple
import math


def generate_vertices(center: Tuple[float, float], radius: float, sides: int) -> List[Tuple[float, float]]:
    """
    Generate coordinates for vertices evenly spaced around a circle.  This
    function serves as a lightweight stand-in for a hypothetical high level
    spatial field (HLSF) adapter.  It returns `sides` points on a circle of
    the given `radius` centered at `center`.  If `sides` is zero or
    negative an empty list is returned.
    """
    if sides <= 0:
        return []
    cx, cy = center
    vertices: List[Tuple[float, float]] = []
    for i in range(sides):
        angle = 2 * math.pi * i / sides
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices