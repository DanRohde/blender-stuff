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
