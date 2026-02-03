from .constants import COLORS
import numpy as np

def get_color(color_idx):
    if color_idx > len(COLORS)-1:
        color = np.random.rand(4)
        color[3] = 1
    else:
        color = COLORS[color_idx]
    return color

def remap(x, in_min, in_max, out_min, out_max):
    return out_min + ((x - in_min) / (in_max - in_min)) * (out_max - out_min)

def get_dimensions(obj):
    from mathutils import Vector
    bbox = [Vector(v) for v in obj.bound_box]
    return (
        max(v.x for v in bbox) - min(v.x for v in bbox),
        max(v.y for v in bbox) - min(v.y for v in bbox),
        max(v.z for v in bbox) - min(v.z for v in bbox)
    )