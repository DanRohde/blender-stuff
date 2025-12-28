import numpy as np
import random


class WFC3DGrid:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.grid = None
        self.collapsed = None
        self.corners = None
        self.edges = None
        self._init_corners()
        self._init_edges()

    def initialize_grid(self, objects, constraints):
        """Initializes the 3D grid"""
        self.grid = np.empty(self.grid_size, dtype=object)
        self.collapsed =  np.empty(self.grid_size)
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    cell = []
                    for obj in objects:
                        if constraints is None or constraints.are_grid_constraints_satisfied(obj.name, (x, y, z)):
                            cell.append(obj.name)

                    self.grid[x, y, z] = cell
                    self.collapsed[x, y, z] = False

    def is_corner(self, pos):
        x, y, z = pos
        l, w, h = self.grid_size
        return x in {0, l - 1} and y in {0, w - 1} and z in {0, h - 1}

    def is_edge(self, pos):
        x, y, z = pos
        l, w, h = self.grid_size
        if self.is_corner(pos):
            return False
        return (x in {0, l - 1} and (y in {0, w - 1} or z in {0, h - 1})) or \
            (y in {0, w - 1} and (x in {0, l - 1} or z in {0, h - 1})) or \
            (z in {0, h - 1} and (x in {0, l - 1} or y in {0, w - 1}))

    def is_inside(self, pos):
        x, y, z = pos
        l, w, h = self.grid_size
        return 0 < x < l - 1 and 0 < y < w - 1 and 0 < z < h - 1

    def is_on_given_edge(self, p, edge):
        if edge not in self.edges: return True
        a, b = self.edges[edge]
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        px, py, pz = p[0] - a[0], p[1] - a[1], p[2] - a[2]
        t_values = []
        for dp, d in zip((px, py, pz), (dx, dy, dz)):
            if d != 0:
                t_values.append(dp / d)
            else:
                if dp != 0: return False
        if not t_values: return False
        if not all(abs(t - t_values[0]) < 1e-9 for t in t_values): return False
        t = t_values[0]
        return 0 <= t <= 1

    def is_on_given_corner(self, p, corner):
        if corner not in self.corners: return True
        return p == self.corners[corner]

    def is_face(self, pos):
        return not self.is_corner(pos) and not self.is_edge(pos) and not self.is_inside(pos)

    def is_on_specific_face(self, pos, face):
        x, y, z = pos
        l, w, h = self.grid_size
        if face == "top":
            return z == h - 1 and 0 < x < l - 1 and 0 < y < w - 1
        elif face == "bottom":
            return z == 0 and 0 < x < l - 1 and 0 < y < w - 1
        elif face == "left":
            return x == 0 and 0 < y < w - 1 and 0 < z < h - 1
        elif face == "right":
            return x == l - 1 and 0 < y < w - 1 and 0 < z < h - 1
        elif face == "front":
            return y == 0 and 0 < x < l - 1 and 0 < z < h - 1
        elif face == "back":
            return y == w - 1 and 0 < x < l - 1 and 0 < z < h - 1
        else:
            return False

    def within_boundaries(self, x, y, z):
        return 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1] and 0 <= z < self.grid_size[2]

    def is_inside_region(self, pos, rmin, rmax):
        x, y, z = pos
        if rmin is None:
            ax, ay, az = (0, 0, 0)
        else:
            ax, ay, az = rmin
            if ax < 0: ax = 0
            if ay < 0: ay = 0
            if az < 0: az = 0
        if rmax is None:
            bx, by, bz = (self.grid_size[0] - 1, self.grid_size[1] - 1, self.grid_size[2] - 1)
        else:
            bx, by, bz = rmax
            if bx < 0: bx = self.grid_size[0] - 1
            if by < 0: by = self.grid_size[1] - 1
            if bz < 0: bz = self.grid_size[2] - 1

        return ax <= x <= bx and ay <= y <= by and az <= z <= bz

    def get_quadrant(self, pos):
        """ returns the quadrant of pos:
            fbl:0, fbr:1, ftl:2, ftr:3 , bbl:4, bbr:5, btl:6, btr: 7, oob: -1
        """
        x, y, z = pos
        mx, my, mz = self.grid_size[0] - 1, self.grid_size[1] - 1, self.grid_size[2] - 1
        hx, hy, hz = mx / 2, my / 2, mz / 2

        if 0 <= x <= hx and 0 <= y <= hy and 0 <= z <= hz:  return 0 # fbl
        elif hx < x <= mx and 0 <= y <= hy and 0 <= z <= hz:  return 1 # fbr
        elif 0 <= x <= hx and 0 <= y <= hy and hz < z <= mz:  return 2 # ftl
        elif hx < x <= mx and 0 <= y <= hy and hz < z <= mz:  return 3 # ftr
        elif 0 <= x <= hx and hy < y <= my and 0 <= z <= hz:  return 4 # bbl
        elif hx < x <= mx and hy < y <= my and 0 <= z <= hz:  return 5 # bbr
        elif 0 <= x <= hx and hy < y <= my and hz < z <= mz:  return 6 # btl
        elif hx < x <= mx and hy < y <= my and hz < z <= mz:  return 7 # btr
        return -1

    def is_inside_region_quadrant(self, pos, constraint):
        return not constraint or constraint[self.get_quadrant(pos)]

    def count_obj(self, obj_name):
        count = 0
        gx, gy, gz = self.grid_size
        for x in range(gx):
            for y in range(gy):
                for z in range(gz):
                    if self.collapsed[x, y, z] and obj_name in self.grid[x, y, z]: count += 1
        return count

    def count_neighbors(self, x, y, z, neighbor, dirs):
        """count neighbors"""
        count = 0
        for direction, (dx, dy, dz) in dirs.items():
            nx, ny, nz = x + dx, y + dy, z + dz
            if not self.within_boundaries(nx, ny, nz): continue
            if (neighbor is None and len(self.grid[nx, ny, nz]) > 0) or neighbor in self.grid[nx, ny, nz]: count += 1
        return count

    def count_axis_neighbors(self, x, y, z, neighbor, axis):
        """Count objects in a given axis"""
        count = [0, 0, 0]
        xa, ya, za = (1 - axis[0]) * x, (1 - axis[1]) * y, (1 - axis[2]) * z
        while self.within_boundaries(xa, ya, za):
            if xa != x or ya != y or za != z:
                if (neighbor is None and len(self.grid[xa, ya, za]) > 0) or neighbor in self.grid[xa, ya, za]:
                    count[0] += axis[0]
                    count[1] += axis[1]
                    count[2] += axis[2]
            xa, ya, za = xa + axis[0], ya + axis[1], za + axis[2]
        return count
    def count_empty_cells(self):
        count = 0
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    if len(self.grid[x,y,z]) == 0: count+=1
        return count
    def count_empty_cells_in_direction(self, x, y, z, direction):
        count = 0
        xa, ya, za = x + direction[0], y + direction[1], z + direction[2]
        while self.within_boundaries(xa, ya, za):
            if len(self.grid[xa, ya, za]) == 0: count+=1
            xa, ya, za = xa + direction[0], ya + direction[1], za + direction[2]
        return count

    def remove_neighbors(self, x, y, z, neighbor, d):
        """Remove neighbors"""
        reduced_cells = []
        for direction, (dx, dy, dz) in d.items():
            nx, ny, nz = x + dx, y + dy, z + dz
            if not self.within_boundaries(nx, ny, nz): continue
            if neighbor in self.grid[nx, ny, nz]:
                self.grid[nx, ny, nz] = [n for n in self.grid[nx, ny, nz] if n != neighbor]
                reduced_cells.append((nx, ny, nz))
        return reduced_cells

    def remove_axis_neighbors(self, x, y, z, neighbor, axis):
        """Remove neighbors"""
        reduced_cells = []
        xa, ya, za = (1 - axis[0]) * x, (1 - axis[1]) * y, (1 - axis[2]) * z
        while self.within_boundaries(xa, ya, za):
            if (xa != x or ya != y or za != z) and neighbor in self.grid[xa, ya, za]:
                self.grid[xa, ya, za] = [n for n in self.grid[xa, ya, za] if n != neighbor]
                reduced_cells.append((xa, ya, za))
            xa, ya, za = xa + axis[0], ya + axis[1], za + axis[2]
        return reduced_cells

    def remove_max_neighbors(self, x, y, z, max_count, d):
        """Remove max any random neighbor"""
        neighbors_pos = []
        ## collect neighbors
        for direction, (dx, dy, dz) in d.items():
            nx, ny, nz = x + dx, y + dy, z + dz
            if not self.within_boundaries(nx, ny, nz) or len(self.grid[nx, ny, nz]) < 1: continue
            neighbors_pos.append([nx, ny, nz])

        if max_count > len(neighbors_pos): max_count = len(neighbors_pos)

        ## randomize neighbor positions and remove first max_count neighbors
        random.shuffle(neighbors_pos)
        for i in range(max_count):
            dx, dy, dz = neighbors_pos[i]
            self.grid[dx, dy, dz] = []
        return []

    def remove_max_axis_neighbors(self, x, y, z, max_count, axis):
        """Remove max any random axis neighbor"""
        neighbor_pos = []
        xa, ya, za = (1 - axis[0]) * x, (1 - axis[1]) * y, (1 - axis[2]) * z
        while self.within_boundaries(xa, ya, za):
            if ((xa != x or ya != y or za != z) or (max_count == 0)) and len(self.grid[xa, ya, za]) > 0:
                neighbor_pos.append([xa, ya, za])
            xa, ya, za = xa + axis[0], ya + axis[1], za + axis[2]

        if max_count > len(neighbor_pos): max_count = len(neighbor_pos)
        random.shuffle(neighbor_pos)
        for i in range(max_count):
            xa, ya, za = neighbor_pos[i]
            self.grid[xa, ya, za] = []
        return []
    def remove_max_region_neighbors(self, x, y, z, max_count, rmin, rmax):
        if not self.within_boundaries(x,y,z) or self.grid[x,y,z] == 0: return
        xa,ya,za = rmin
        xb,yb,zb = rmax
        if not self.within_boundaries(xa, ya, za) or not self.within_boundaries(xb, yb, zb): return
        obj_name = self.grid[x,y,z][0]
        npos = []
        for dx in range(xb-xa+1):
            for dy in range(yb-ya+1):
                for dz in range(zb-za+1):
                    if xa+dx == x and ya+dy == y and za+dz == z: continue
                    if obj_name in self.grid[xa+dx, ya+dy, za+dz]: npos.append([xa+dx, ya+dy, za+dz])

        if len(npos) < max_count: return
        if max_count == 0: npos.append([x,y,z])
        if len(npos)-max_count+1 > len(npos): max_count += 1
        random.shuffle(npos)
        for i in range(len(npos)-max_count+1):
            xa, ya, za = npos[i]
            self.grid[xa, ya, za] = [ n for n in self.grid[xa,ya,za] if n!=obj_name ]

    def remove_obj_in_region(self, obj_name, min_position, max_position, ignore_position = None):
        for x in range(min_position[0], max_position[0]+1):
            for y in range(min_position[1], max_position[1]+1):
                for z in range(min_position[2], max_position[2]+1):
                    if self.collapsed[x, y, z]: continue
                    if self.within_boundaries(x, y, z) and (ignore_position is None or ignore_position[0]!=x or ignore_position[1]!=y or ignore_position[2]!=z):
                        new_options = [n for n in self.grid[x,y,z] if n != obj_name ]
                        self.grid[x,y,z] = new_options
    def remove_obj_outside_region(self, obj_name, min_position, max_position):
        min_x, min_y, min_z = min_position
        max_x, max_y, max_z = max_position
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    if self.collapsed[x, y, z]: continue
                    if min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z: continue
                    new_options = [n for n in self.grid[x, y, z] if n != obj_name]
                    self.grid[x, y, z] = new_options

    def remove_obj(self, obj_name):
        gx, gy, gz = self.grid_size
        for x in range(gx):
            for y in range(gy):
                for z in range(gz):
                    if not self.collapsed[x, y, z] and obj_name in self.grid[x, y, z]:
                        self.grid[x, y, z] = [n for n in self.grid[x, y, z] if n != obj_name]

    def mark_collapsed(self, x, y, z):
        self.collapsed[x, y, z] = True
        return x, y, z

    def fix_position(self, position):
        if position is None: return 0, 0, 0
        x, y, z = position
        mx, my, mz = self.grid_size[0]-1, self.grid_size[1]-1, self.grid_size[2]-1
        if x < 0: x = mx + x
        if y < 0: y = my + y
        if z < 0: z = mz + z
        return max(min(x, mx), 0), max(min(y, my), 0), max(min(z, mz), 0)

    @staticmethod
    def _mult_vector(v1, v2):
        return tuple(a * b for a, b in zip(v1, v2))

    def _init_corners(self):
        gs = (self.grid_size[0] - 1, self.grid_size[1] - 1, self.grid_size[2] - 1)
        self.corners = {
            'fbl': (0, 0, 0),
            'fbr': self._mult_vector((1, 0, 0), gs),
            'ftl': self._mult_vector((0, 0, 1), gs),
            'ftr': self._mult_vector((1, 0, 1), gs),
            'bbl': self._mult_vector((0, 1, 0), gs),
            'bbr': self._mult_vector((1, 1, 0), gs),
            'btl': self._mult_vector((0, 1, 1), gs),
            'btr': self._mult_vector((1, 1, 1), gs),
        }

    def _init_edges(self):
        c = self.corners
        self.edges = {
            'fb': (c['fbl'], c['fbr']),
            'fl': (c['fbl'], c['ftl']),
            'ft': (c['ftl'], c['ftr']),
            'fr': (c['fbr'], c['ftr']),
            'bb': (c['bbl'], c['bbr']),
            'bl': (c['bbl'], c['btl']),
            'bt': (c['btl'], c['btr']),
            'br': (c['bbr'], c['btr']),
            'lb': (c['fbl'], c['bbl']),
            'lt': (c['ftl'], c['btl']),
            'rb': (c['fbr'], c['bbr']),
            'rt': (c['ftr'], c['btr']),
        }
    def clean(self):
        self.grid = None
        self.collapsed = None
        self.grid_size = None
        self.edges = None
        self.corners = None