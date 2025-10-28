import bpy
import random

from .constraints import WFC3DConstraints
from .grid import WFC3DGrid
from .constants import DEFAULT_EMPTY_NAME

class WFC3DGenerator:
    def __init__(self, collection, props):
        self.collection = collection
        self.grid_size = props.grid_size
        self.spacing = props.spacing
        self.use_constraints = props.use_constraints
        self.target_collection = props.target_collection
        self.target_collection_obj = None
        self.link_objects = props.link_objects
        self.copy_modifiers = props.copy_modifiers
        self.random_start_cell = props.random_start_cell
        self.render_delay = props.render_delay
        self.collapsed_cells = []
        self.odd_offset = props.odd_offset

        random.seed(props.seed)
        self.remove_target_collection = props.remove_target_collection
        self.objects = []
        self.constraints = None
        self.load_objects()

        self.grid = WFC3DGrid(self.grid_size)

        if self.use_constraints:
            self.constraints = WFC3DConstraints()
            self.constraints.initialize_constraints(self.grid, self.collection, self.objects)
                    

    def load_objects(self):
        """Loads objects from the collection"""
        self.objects = [ obj for obj in self.collection.objects if not obj.name.startswith(DEFAULT_EMPTY_NAME)]
        self.objects.extend([child for child in self.collection.children if len(child.objects)>0])
        if not self.objects:
            raise ValueError("Collection is empty!")

    
    def get_entropy(self, x, y, z):
        """Calculates the entropy (number of possible states) of a cell"""
        return len(self.grid.grid[x, y, z])

    def get_lowest_entropy_cell(self):
        """Finds the cell with the lowest entropy"""
        min_entropy = float('inf')
        min_cells = {}
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    if self.grid.collapsed[x, y, z]: continue
                    entropy = self.get_entropy(x, y, z)
                    if entropy > min_entropy: continue
                    min_entropy = entropy
                    min_cell = (x, y, z)
                    if min_entropy in min_cells:
                        min_cells[min_entropy].append(min_cell)
                    else:
                        min_cells[min_entropy] = [ min_cell ]

        if len(min_cells) == 0: return None
        
        if self.random_start_cell:
            return random.choice(min_cells[min_entropy])
        else:
            return min_cells[min_entropy][0]
        
    def collapse(self, x, y, z):
        """Collapses a cell into a single state"""
        if self.use_constraints:
            collapsed = self.constraints.collapse(self.grid, x, y, z)
        else:
            self.grid.grid[x, y, z] = [random.choice(self.grid.grid[x,y,z])]
            collapsed = [ self.grid.mark_collapsed(x, y, z) ]
        return collapsed

    def generate_model(self):
        """Execute WFC algorithm and generate the model"""
        self.grid.initialize_grid(self.objects, self.constraints)
        self.init_target_collection()
        while True:
            cell = self.get_lowest_entropy_cell()
            if cell is None:
                break    
            x, y, z = cell
            collapsed = self.collapse(x, y, z)

            self.collapsed_cells.extend(collapsed)
            if self.use_constraints:
                self.constraints.propagate(self.grid, x, y, z)

        if self.render_delay > 0:
            bpy.context.scene.wfc_props.running_delayed_renderer = True
            bpy.app.timers.register(self.place_delayed_objects, first_interval=self.render_delay)
        else:
            while len(self.collapsed_cells)>0:
                self.place_object(self.collapsed_cells.pop(0))

    def place_delayed_objects(self):
        if not bpy.context.scene.wfc_props.running_delayed_renderer:
            return None
        if len(self.collapsed_cells) > 0 and not bpy.context.scene.wfc_props.paused_delayed_renderer:
            self.place_object(self.collapsed_cells.pop(0))

        if len(self.collapsed_cells) > 0:
            return self.render_delay
        else:
            bpy.context.scene.wfc_props.running_delayed_renderer = False
            bpy.context.scene.wfc_props.paused_delayed_renderer = False
            def draw(self, _context):
                self.layout.label(text="WFC 3D model successfully rendered!")
            bpy.context.window_manager.popup_menu(draw, title="Info", icon='INFO')
        return None

    def init_target_collection(self):
        collection_name = self.target_collection
        if self.remove_target_collection and collection_name in bpy.data.collections:
            bpy.data.collections.remove(bpy.data.collections[collection_name])
        self.target_collection_obj = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(self.target_collection_obj)

    def place_object(self, pos):
        x, y, z = pos
        if len(self.grid.grid[x, y, z]) > 0:
            obj_name = self.grid.grid[x, y, z][0]
        else:
            return

        collection = self.target_collection_obj

        # pick random  objects from a collection
        if obj_name in bpy.data.collections:
            c = bpy.data.collections[obj_name]
            original_obj = random.choice([o for o in c.objects if not o.name.startswith(DEFAULT_EMPTY_NAME)])
        else:
            original_obj = next((obj for obj in self.objects if obj.name == obj_name), None)

        if original_obj:
            if self.link_objects:
                new_obj = bpy.data.objects.new(name=original_obj.name, object_data=original_obj.data)
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

            newloc = [x * self.spacing[0] + (self.odd_offset[0] * (y % 2)), y * self.spacing[1] + (self.odd_offset[1] * (x % 2)), z * self.spacing[2] + (self.odd_offset[2] * (x % 2))]

            new_obj.location = tuple(newloc)

            if self.use_constraints:
                self.constraints.apply_transformation_constraints((x, y, z), obj_name, new_obj)

            collection.objects.link(new_obj)