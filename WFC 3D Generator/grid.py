import numpy as np
class WFC3DGrid:
    def __init__(self, grid_size):
        self.grid_size = grid_size;        
        self.grid = None
        self._init_corners()
        self._init_edges()
        
    def initialize_grid(self, objects, constraints):
        """Initializes the 3D grid"""
        self.grid = np.empty(self.grid_size, dtype=object)
        self.collapsed = np.empty(self.grid_size)
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    cell = []
                    for obj in objects:
                        if constraints is None or self.are_grid_constraints_satisfied(obj.name, constraints.constraints, (x, y, z)):
                            cell.append(obj.name)
                    
                    self.grid[x, y, z] = cell
                    self.collapsed[x, y, z] = False
    
    def is_corner(self, pos):
        x, y, z = pos
        l, w, h = self.grid_size
        return (x in {0, l-1} and y in {0, w-1} and z in {0, h-1})
    
    def is_edge(self, pos):
        x, y, z = pos
        l, w, h = self.grid_size
        if self.is_corner(pos):
            return False
        return (x in {0, l-1} and (y in {0, w-1} or z in {0, h-1})) or \
               (y in {0, w-1} and (x in {0, l-1} or z in {0, h-1})) or \
               (z in {0, h-1} and (x in {0, l-1} or y in {0, w-1}))
    
    def is_inside(self, pos):
        x, y, z = pos
        l, w, h = self.grid_size
        return 0 < x < l-1 and 0 < y < w-1 and 0 < z < h-1
    
    def is_on_given_edge(self, p, edge):
        a,b = edge
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        px, py, pz = p[0] - a[0], p[1] - a[1], p[2] - a[2]
        t_values = []
        for dp, d in zip((px, py, pz), (dx, dy, dz)):
            if d != 0:
                t_values.append(dp / d)
            else:
                if dp != 0:
                    return False    
        if not t_values:
            return False  
        if not all(abs(t - t_values[0]) < 1e-9 for t in t_values):
            return False    
        t = t_values[0]
        return 0 <= t <= 1

    def is_face(self, pos):
        x, y, z = pos
        l, w, h = self.grid_size
        return not self.is_corner(pos) and not self.is_edge(pos) and not self.is_inside(pos)
    
    def is_on_specific_face(self, pos, face):
        x, y, z = pos
        l, w, h = self.grid_size
        if face == "top":
            return z == h-1 and 0 < x < l-1 and 0 < y < w-1
        elif face == "bottom":
            return z == 0 and 0 < x < l-1 and 0 < y < w-1
        elif face == "left":
            return x == 0 and 0 < y < w-1 and 0 < z < h-1
        elif face == "right":
            return x == l-1 and 0 < y < w-1 and 0 < z < h-1
        elif face == "front":
            return y == 0 and 0 < x < l-1 and 0 < z < h-1
        elif face == "back":
            return y == w-1 and 0 < x < l-1 and 0 < z < h-1
        else:
            return False

    def within_boundaries(self, x, y, z):
        return 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1] and 0 <= z < self.grid_size[2]

    def are_grid_constraints_satisfied(self, name, constraints, pos):
        if 'corners' in constraints[name] and self.is_corner(pos):
            for c in constraints[name]['corners']:
                if c == '' and len(constraints[name]['corners'])==1:
                    return True
                if c == '-' or c == 'None' or c == 'False':
                    return False
                if c in self.corners and pos == self.corners[c]:
                    return True
            return False
        if 'edges' in constraints[name] and self.is_edge(pos):
            for c in constraints[name]['edges']:
                if c == '' and len(constraints[name]['edges'])==1:
                    return True
                if c == '-' or c == 'None':
                    return False
                if c in self.edges and self.is_on_given_edge(pos, self.edges[c]):
                    return True
            return False
        if 'inside' in constraints[name] and self.is_inside(pos):
            inside = constraints[name]['inside']
            if inside == '' or inside == 'True':
                return True
            if inside == '-' or inside == 'None' or inside == 'False':
                return False
            return False
        if 'faces' in constraints[name] and self.is_face(pos):
            for f in constraints[name]['faces']:
                if f == '' and len(constraints[name]['faces'])==1:
                    return True
                if f == '-' or f == 'None' or f == 'False':
                    return False
                if self.is_on_specific_face(pos,f):
                    return True
            return False
        return True

    def count_obj(self, obj_name, pos, dir, steps):
        count = 0
        gx, gy, gz = self.grid_size
        if pos and dir:
            x, y, z = pos
            dx, dy, dz = dir
            stepcounter = 0
            while (0 <= x+dx < gx and 0 <= y+dy < gy and 0<= z+dz < gz and stepcounter < steps):
                stepcounter+=1
                if obj_name in self.grid[x+dx, y+dy, z+dz] and self.collapsed[x+dx, y+dy, z+dz]:
                    count+=1
                    x,y,z = x+dx, y+dy, z+dz
        else:
            for x in range(gx):
                for y in range(gy):
                    for z in range(gz):
                        if obj_name in self.grid[x, y, z] and self.collapsed[x,y,z]:
                            count+=1
        
        return count

    def remove_obj(self, obj_name, pos, dir):
        gx, gy, gz = self.grid_size
        deleted = 0
        if pos and dir:
            x,y,z = pos
            dx, dy, dz = dir
            while (0 <= x+dx < gx and 0 <= y+dy < gy and 0 <= z+dz < gz):
                obj_list = self.grid[x+dx,y+dy,z+dz]
                if obj_name in obj_list and not self.collapsed[x, y, z]:
                    self.grid[x+dx,y+dy,z+dz] = [n for n in obj_list if n != obj_name]
                    deleted+=1
            return deleted
        else:
            for x in range(gx):
                for y in range(gy):
                    for z in range(gz):
                        obj_list = self.grid[x, y, z]
                        if obj_name in obj_list and not self.collapsed[x,y,z]:
                            self.grid[x, y, z] = [n for n in obj_list if n != obj_name]
                            deleted=+1
        return deleted
    def mark_collapsed(self, x, y, z):
        self.collapsed[x,y,z] = True
    
    def _mult_vector(self, v1, v2):
        return tuple(a * b for a, b in zip(v1,v2))
    
    def _init_corners(self):
        gs = (self.grid_size[0]-1, self.grid_size[1]-1, self.grid_size[2]-1)
        self.corners = {
            'fbl' : (0,0,0),
            'fbr' : self._mult_vector((1,0,0), gs),
            'ftl' : self._mult_vector((0,0,1), gs),
            'ftr' : self._mult_vector((1,0,1), gs),
            'bbl' : self._mult_vector((0,1,0), gs),
            'bbr' : self._mult_vector((1,1,0), gs),
            'btl' : self._mult_vector((0,1,1), gs),
            'btr' : self._mult_vector((1,1,1), gs),
        }

    def _init_edges(self):
        c = self.corners
        self.edges = {
            'fb' : (c['fbl'],c['fbr']),
            'fl' : (c['fbl'],c['ftl']),
            'ft' : (c['ftl'],c['ftr']),
            'fr' : (c['fbr'],c['ftr']),
            'bb' : (c['bbl'],c['bbr']),
            'bl' : (c['bbl'],c['btl']),
            'bt' : (c['btl'],c['btr']),
            'br' : (c['bbr'],c['btr']),
            'lb' : (c['fbl'],c['bbl']),
            'lt' : (c['ftl'],c['btl']),
            'rb' : (c['fbr'],c['bbr']),
            'rt' : (c['ftr'],c['btr']),
        }
