import bpy
from collections import deque
import random
import numpy as np
from .constants import DIRECTIONS, TRANSFORMATION_CONSTRAINTS

class WFC3DConstraints:
    
    def __init__(self):
        self.constraints = {}
    
    def initialize_constraints(self, objects):
        """Loads constraints from custom properties"""
        allobjects = [o.name for o in objects]
        for obj in objects:
            obj_name = obj.name
            self.constraints[obj_name] = {}
            
            if obj.name in bpy.data.collections:
                    obj = bpy.data.collections[obj.name].objects[0]
                
            # load weight constraints
            if "wfc_weight" in obj and obj["wfc_weight"] != "":
                self.constraints[obj_name]["weight"] = int(obj["wfc_weight"])
            else:
                self.constraints[obj_name]["weight"] = 1

            # load grid constraints
            grid_constraints = { 'wfc_corners':'corners', 'wfc_edges':'edges', 'wfc_inside':'inside','wfc_faces' :'faces' }
            for gc in grid_constraints:
                if gc in obj and obj[gc] != "":
                    self.constraints[obj_name][grid_constraints[gc]] = obj[gc].split(",")
            
            # load transformation constraints
            for r in TRANSFORMATION_CONSTRAINTS:
                if "wfc_"+r in obj:
                    self.constraints[obj_name][r] = obj["wfc_"+r]
                else:
                    self.constraints[obj_name][r] = None
                    
            
            # load neighbor constraints
            for direction in DIRECTIONS:
                prop_name = f"wfc_{direction.lower()}"
                # take first element from collection to get constraints
                if prop_name in obj:
                    if obj[prop_name] == "":
                        self.constraints[obj_name][direction] = allobjects
                    else:
                        self.constraints[obj_name][direction] = obj[prop_name].split(',')
                else:
                    self.constraints[obj.name][direction] = allobjects 
    def apply_transformation_constraints(self, src_obj, target_obj):
        def _get_mapped_random_values(min, max, steps):
            if (steps < 0 and min > max):
                steps =- steps
                s = max
                max = min 
                min = s
                
            if (steps > 0 and max-min >= 0):
                v = []
                i = min
                while i<=max:
                    v.append(i)
                    i += steps
                if (i-steps < max):
                     v.append(max)   
                return v[random.randrange(0,len(v))]
            else:
                return min + (max-min) * random.random()
        constraints = self.constraints[src_obj.name]    
        if constraints["translation_min"] is not None and constraints["translation_max"] is not None and constraints["translation_steps"] is not None:
            tmin = constraints["translation_min"]
            tmax = constraints["translation_max"]
            ts = constraints["translation_steps"]
            loc = target_obj.location
            for i in range(3):
                loc[i]+=_get_mapped_random_values(tmin[i], tmax[i], ts[i])
            target_obj.location = loc
        
        if constraints["scale_type"] is not None and constraints["scale_type"] > 0:
            
            if constraints["scale_type"] == 1 and constraints["scale_uni"] is not None:
                s = _get_mapped_random_values(constraints["scale_uni"][0], constraints["scale_uni"][1], constraints["scale_uni"][2])
                target_obj.scale.x = s 
                target_obj.scale.y = s
                target_obj.scale.z = s
            if constraints["scale_type"] == 2 and constraints["scale_min"] is not None and constraints["scale_max"] is not None and constraints["scale_steps"] is not None:
                smin = constraints["scale_min"]
                smax = constraints["scale_max"]
                ss = constraints["scale_steps"]
                
                target_obj.scale.x = _get_mapped_random_values(smin[0], smax[0], ss[0])
                target_obj.scale.y = _get_mapped_random_values(smin[1], smax[1], ss[1])
                target_obj.scale.z = _get_mapped_random_values(smin[2], smax[2], ss[2])
        
        if constraints["rotation_min"] is not None and constraints["rotation_max"] is not None and constraints["rotation_steps"] is not None:
            rmin = constraints["rotation_min"]
            rmax = constraints["rotation_max"]
            rs = constraints["rotation_steps"]
            
            axis=['X','Y','Z']
            for i in range(3):
                a = _get_mapped_random_values(rmin[i], rmax[i], rs[i])
                if a!=0:
                    target_obj.rotation_euler.rotate_axis(axis[i], a)
        
            
class WFC3DGrid:
    def __init__(self, grid_size):
        self.grid_size = grid_size;        
        self.grid = None
        self._init_corners()
        self._init_edges()
        
    def initialize_grid(self, objects, constraints):
        """Initializes the 3D grid"""
        self.grid = np.empty(self.grid_size, dtype=object)
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    cell = []
                    for obj in objects:
                        if constraints is None or self.are_grid_constraints_satisfied(obj.name, constraints, (x, y, z)):
                            cell.append(obj.name)
                    
                    self.grid[x, y, z] = cell
    
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

    def count_obj(self, obj_name, pos, dir):
        count = 0
        x, y, z = pos
        dx, dy, dz = dir
        gx, gy, gz = self.grid_size
        while (0 <= x+dx < gx and 0 <= y+dy < gy and 0<= z+dz < gz):
            if obj_name in self.grid[x+dx,y+dy,z+dz] and len(self.grid[x+dx,y+dy,z+dz])>1:
                count+=1
            x,y,z = x+dx, y+dy, z+dz
        return count
    def remove_obj(self, obj_name, pos, dir, count):
        x,y,z = pos
        dx, dy, dz = dir    
        gx, gy, gz = self.grid_size
        deleted = 0
        while (0 <= x+dx < gx and 0 <= y+dy < gy and 0 <= z+dz < gz and deleted < count):
            obj_list = self.grid[x+dx,y+dy,z+dz]
            if obj_name in obj_list and len(obj_list)>1:
                self.grid[x+dx,y+dy,z+dz] = [n for n in obj_list if n !=obj_name]
                deleted+=1
        return deleted

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

class WFC3DGenerator:
    def __init__(self, collection, props):
        self.collection = collection
        self.grid_size = props.grid_size
        self.spacing = props.spacing
        self.use_constraints = props.use_constraints
        self.target_collection = props.target_collection
        self.link_objects = props.link_objects
        self.copy_modifiers = props.copy_modifiers
        
        random.seed(props.seed)
        self.remove_target_collection = props.remove_target_collection
        self.objects = []
        self.constraints = None
        self.load_objects()

        if self.use_constraints:
            self.constraints_obj = WFC3DConstraints()
            self.constraints_obj.initialize_constraints(self.objects)
            self.constraints = self.constraints_obj.constraints
            
        
        self.grid = WFC3DGrid(self.grid_size)

    def load_objects(self):
        """Loads objects from the collection"""
        self.objects = list(self.collection.objects)
        self.objects.extend(self.collection.children)
        if not self.objects:
            raise ValueError("Collection is empty!")

    
    def get_entropy(self, x, y, z):
        """Calculates the entropy (number of possible states) of a cell"""
        return len(self.grid.grid[x, y, z])

    def get_lowest_entropy_cell(self):
        """Finds the cell with the lowest entropy"""
        min_entropy = float('inf')
        min_cell = None
        
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    if self.get_entropy(x, y, z) > 1:
                        entropy = self.get_entropy(x, y, z)
                        if entropy < min_entropy:
                            min_entropy = entropy
                            min_cell = (x, y, z)
        return min_cell

    def get_weighted_options(self, obj_names):
        """ Increase object count in object list depending on it's weight """
        options = []
        for name in obj_names:
            weight = self.constraints[name]['weight']
            option = [name for _ in range(weight)]
            options.extend(option)
        return options
        
    def collapse(self, x, y, z):
        """Collapses a cell into a single state"""
        if self.use_constraints:
            options = self.get_weighted_options(self.grid.grid[x, y, z])
        else:
            options = self.grid.grid[x,y,z]
            
        chosen = random.choice(options)
        self.grid.grid[x, y, z] = [chosen]

    def propagate(self, x, y, z):
        """Propagate constraints to neighbors"""
        queue = deque([(x, y, z)])
        
        while queue:
            cx, cy, cz = queue.popleft()
            if len(self.grid.grid[cx,cy,cz])>0:
                current_obj = self.grid.grid[cx, cy, cz][0]
            else:
                continue
            
            for direction, (dx, dy, dz) in DIRECTIONS.items():
                nx, ny, nz = cx + dx, cy + dy, cz + dz             
                if 0 <= nx < self.grid_size[0] and \
                   0 <= ny < self.grid_size[1] and \
                   0 <= nz < self.grid_size[2]:
                    neighbor_options = self.grid.grid[nx, ny, nz]
                    if len(neighbor_options) > 1:
                        # Find permitted neighbors for this direction
                        allowed = self.constraints[current_obj].get(direction, [])
                        # Filter disallowed options
                        new_options = [obj for obj in neighbor_options if obj in allowed]
                        if len(new_options) < len(neighbor_options):
                            self.grid.grid[nx, ny, nz] = new_options
                            queue.append((nx, ny, nz))


    def generate_model(self):
        """Excecute WFC algorithm and generate the model"""
        self.grid.initialize_grid(self.objects, self.constraints)
        
        while True:
            cell = self.get_lowest_entropy_cell()
            if cell is None:
                break
                
            x, y, z = cell
            self.collapse(x, y, z)
            if self.use_constraints:
                self.propagate(x, y, z)
        
        self.place_objects()

    def place_objects(self):
        """Place the objects in 3D space"""
        # Create a new collection for the result
        collection_name = self.target_collection
        if self.remove_target_collection and collection_name in bpy.data.collections:
            bpy.data.collections.remove(bpy.data.collections[collection_name])
        
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(new_collection)
        
        
        # Place objects
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    if len(self.grid.grid[x,y,z]) > 0:
                        obj_name = self.grid.grid[x, y, z][0]
                    else:
                        continue
                    # pick random  objects from a collection
                    if obj_name in bpy.data.collections:
                        c = bpy.data.collections[obj_name]
                        original_obj = random.choice(c.objects)
                    else:
                        original_obj = next((obj for obj in self.objects if obj.name == obj_name), None)
                    
                    if original_obj:
                        if self.link_objects:
                            new_obj = bpy.data.objects.new(name=original_obj.name, object_data = original_obj.data)
                            if self.copy_modifiers:
                                for mod in original_obj.modifiers:
                                    new_mod = new_obj.modifiers.new(name=mod.name, type=mod.type)
                                    for attr in dir(mod):
                                        if attr.startswith("_"):
                                            continue
                                        try:
                                            setattr(new_mod, attr, getattr(mod, attr))
                                        except Exception:
                                            pass
                        else:
                            new_obj = original_obj.copy()
                            new_obj.data = original_obj.data.copy()
                            
                        newloc = [ x * self.spacing[0],  y * self.spacing[1], z * self.spacing[2] ]                        
                        new_obj.location = tuple(newloc)        

                        if self.use_constraints:
                            self.constraints_obj.apply_transformation_constraints(original_obj, new_obj)
                            
                        new_collection.objects.link(new_obj)

