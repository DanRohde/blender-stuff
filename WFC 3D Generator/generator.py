import bpy
import random

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
        self.random_start_cell = props.random_start_cell
        
        random.seed(props.seed)
        self.remove_target_collection = props.remove_target_collection
        self.objects = []
        self.constraints = None
        self.load_objects()

        if self.use_constraints:
            self.constraints = WFC3DConstraints()
            self.constraints.initialize_constraints(self.objects)
                    
        self.grid = WFC3DGrid(self.grid_size)

    def load_objects(self):
        """Loads objects from the collection"""
        self.objects = list(self.collection.objects)
        self.objects.extend([child for child in self.collection.children if len(child.objects)>0])
        if not self.objects:
            raise ValueError("Collection is empty!")

    
    def get_entropy(self, x, y, z):
        """Calculates the entropy (number of possible states) of a cell"""
        return len(self.grid.grid[x, y, z])

    def get_lowest_entropy_cell(self):
        """Finds the cell with the lowest entropy"""
        min_entropy = float('inf')
        min_cell = None
        min_cells = {}
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    if not self.grid.collapsed[x, y, z]:
                        entropy = self.get_entropy(x, y, z)
                        if entropy <= min_entropy:
                            min_entropy = entropy
                            min_cell = (x, y, z)
                            if min_entropy in min_cells:
                                min_cells[min_entropy].append(min_cell)
                            else:
                                min_cells[min_entropy] = [ min_cell ]

        if len(min_cells) == 0:
            return None
        
        if self.random_start_cell:
            return random.choice(min_cells[min_entropy])
        else:
            return min_cells[min_entropy][0]
        
    def collapse(self, x, y, z):
        """Collapses a cell into a single state"""
        if self.use_constraints:
            self.constraints.collapse(self.grid, x, y, z)
        else:
            self.grid.grid[x, y, z] = [random.choice(self.grid.grid[x,y,z])]
            self.grid.mark_collapsed(x, y, z)

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
                self.constraints.propagate(self.grid, x, y, z)
        
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
                            self.constraints.apply_transformation_constraints(original_obj, new_obj)
                            
                        new_collection.objects.link(new_obj)

