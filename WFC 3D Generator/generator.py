import bpy
from collections import deque
import random
from .constants import DIRECTIONS
from .constraints import WFC3DConstraints
from .grid import WFC3DGrid



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

