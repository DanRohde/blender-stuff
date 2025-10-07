# Written 2025 by Dan Rohde
# To make this add-on installable, create an extension with it:
# https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html

import bpy
import numpy as np
from collections import deque
import random

DIRECTIONS = {
    'TOP': (0, 0, 1),
    'BOTTOM': (0, 0, -1),
    'FRONT': (0, 1, 0),
    'BACK': (0, -1, 0),
    'LEFT': (-1, 0, 0),
    'RIGHT': (1, 0, 0)
}

class WFC3DProperties(bpy.types.PropertyGroup):
    collection_name: bpy.props.StringProperty(
        name="",
        description="Object collection",
        default="WFC_Objects",
    )
    grid_size: bpy.props.IntVectorProperty(
        name="",
        description="Size of the 3D grid",
        size=3,
        default=(5, 5, 5),
        min=1,
        max=100,
    )
    spacing: bpy.props.FloatProperty(
        name="Grid Space",
        description="Size of a Grid element",
        subtype="DISTANCE",
        default=2.0,
        min=0.1,
    )
    use_constraints: bpy.props.BoolProperty(
        name="Use Neighbor Constraints",
        description="Use constraints",
        default=True,
    )
    empty_constraints: bpy.props.BoolProperty(
        name="Create Empty Constraint Properties",
        description="Default: a comma separated list of all object names in the collection",
        default=False,
    )
    overwrite_constraints: bpy.props.BoolProperty(
        name="Overwrite Existing Constraint Properties",
        description="Overwrite existing object constraints in Custom Properties",
        default=False,
    )
    target_collection: bpy.props.StringProperty(
        name="",
        description="Target collection for 3D grid",
        default="WFC_Generated",
    )
    seed: bpy.props.IntProperty(
        name="Random Seed",
        description="Random seed",
        default=0,
    )
    link_objects: bpy.props.BoolProperty(
        name="Link New Objects (recommended)",
        description="Link new objects instead of copying them.",
        default=True,
    )
    remove_target_collection: bpy.props.BoolProperty(
        name="Remove Target Collection",
        description="Remove existing target collection",
        default=False,
    )

class WFC3DGenerator:
    def __init__(self, collection, props):
        self.collection = collection
        self.grid_size = props.grid_size
        self.spacing = props.spacing
        self.use_constraints = props.use_constraints
        self.target_collection = props.target_collection
        self.link_objects = props.link_objects
        random.seed(props.seed)
        self.remove_target_collection = props.remove_target_collection
        self.grid = None
        self.objects = []
        self.constraints = {}
        self.load_objects()
        self.load_constraints()


    def load_objects(self):
        """Loads objects from the collection"""
        self.objects = list(self.collection.objects)
        if not self.objects:
            raise ValueError("Collection is empty!")

    def load_constraints(self):
        """Loads neighbor relations from custom properties"""
        for obj in self.objects:
            self.constraints[obj.name] = {}
            for direction in DIRECTIONS:
                prop_name = f"wfc_{direction.lower()}"
                if prop_name in obj:
                    if obj[prop_name] == "":
                        self.constraints[obj.name][direction] = [o.name for o in self.objects]
                    else:
                        self.constraints[obj.name][direction] = obj[prop_name].split(',')
                else:
                    # Standard: Alle Objekte erlaubt
                    self.constraints[obj.name][direction] = [o.name for o in self.objects]

    def initialize_grid(self):
        """Initializes the 3D grid with superpositions"""
        self.grid = np.empty(self.grid_size, dtype=object)
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    self.grid[x, y, z] = [obj.name for obj in self.objects]

    def get_entropy(self, x, y, z):
        """Calculates the entropy (number of possible states) of a cell"""
        return len(self.grid[x, y, z])

    def get_lowest_entropy_cell(self):
        """Finds the cell with the lowest entropy"""
        min_entropy = float('inf')
        min_cell = None
        
        for z in range(self.grid_size[2]):
            for x in range(self.grid_size[0]):
                for y in range(self.grid_size[1]):
                    if self.get_entropy(x, y, z) > 1:
                        entropy = self.get_entropy(x, y, z)
                        if entropy < min_entropy:
                            min_entropy = entropy
                            min_cell = (x, y, z)
        return min_cell

    def collapse(self, x, y, z):
        """Collapses a cell into a single state"""
        options = self.grid[x, y, z]
        chosen = random.choice(options)
        self.grid[x, y, z] = [chosen]

    def propagate(self, x, y, z):
        """Propagate constraints to neighbors"""
        queue = deque([(x, y, z)])
        
        while queue:
            cx, cy, cz = queue.popleft()
            if len(self.grid[cx,cy,cz])>0:
                current_obj = self.grid[cx, cy, cz][0]
            else:
                continue
            for direction, (dx, dy, dz) in DIRECTIONS.items():
                nx, ny, nz = cx + dx, cy + dy, cz + dz
                
                if 0 <= nx < self.grid_size[0] and \
                   0 <= ny < self.grid_size[1] and \
                   0 <= nz < self.grid_size[2]:
                    neighbor_options = self.grid[nx, ny, nz]
                    if len(neighbor_options) > 1:
                        # Find permitted neighbors for this direction
                        opposite_dir = self.get_opposite_direction(direction)
                        allowed = self.constraints[current_obj].get(opposite_dir, [])
                        
                        # Filter disallowed options
                        new_options = [obj for obj in neighbor_options if obj in allowed]
                        
                        if len(new_options) < len(neighbor_options):
                            self.grid[nx, ny, nz] = new_options
                            queue.append((nx, ny, nz))

    def get_opposite_direction(self, direction):
        """Returns oposite direction"""
        opposites = {
            'TOP': 'BOTTOM',
            'BOTTOM': 'TOP',
            'FRONT': 'BACK',
            'BACK': 'FRONT',
            'LEFT': 'RIGHT',
            'RIGHT': 'LEFT'
        }
        return opposites[direction]

    def generate_model(self):
        """Excecute WFC algorithm and generate the model"""
        self.initialize_grid()
        
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
                    if len(self.grid[x,y,z]) > 0:
                        obj_name = self.grid[x, y, z][0]
                    else:
                        continue
                    original_obj = next((obj for obj in self.objects if obj.name == obj_name), None)
                    
                    
                    if original_obj:
                        if self.link_objects:
                            new_obj = bpy.data.objects.new(name=original_obj.name, object_data = original_obj.data)
                        else:
                            new_obj = original_obj.copy()
                            new_obj.data = original_obj.data.copy()
                        new_obj.location = (
                            x * self.spacing,
                            y * self.spacing,
                            z * self.spacing,
                        )
                        new_collection.objects.link(new_obj)

class OBJECT_OT_WFC3DGenerate(bpy.types.Operator):
    """Generates a 3D model with Wave Function Collapse"""
    bl_idname = "object.wfc_3d_generate"
    bl_label = "Generate WFC 3D Model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute_prod(self, context):
        props = context.scene.wfc_props
        
        try:
            collection = bpy.data.collections.get(props.collection_name)
            if not collection:
                raise ValueError(f"Collection '{props.collection_name}' not found!")
                
            generator = WFC3DGenerator(collection, props)
            generator.generate_model()
            
            self.report({'INFO'}, "WFC model successfully generated!")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}",)
            return {'CANCELLED'}
    def execute(self, context):
        props = context.scene.wfc_props
        
        collection = bpy.data.collections.get(props.collection_name)
        if not collection:
            raise ValueError(f"Collection '{props.collection_name}' not found!")
                
        generator = WFC3DGenerator(collection, props)
        generator.generate_model()
            
        self.report({'INFO'}, "WFC model successfully generated!")
        return {'FINISHED'}
        
class OBJECT_OT_WFC3DCollectionInit(bpy.types.Operator):
    """Initialize object constraints"""
    bl_idname="object.wfc_3d_init_collection"
    bl_label = "Initialize Constraint Properties"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        try:
            collection = bpy.data.collections.get(props.collection_name)
            if not collection:
                raise ValueError(f"Collection '{props.collection_name}' not found!")
            objects = list(collection.objects)
            if not objects:
                raise ValueError("Collection is empty!")
            
            if props.empty_constraints:
                all_object_names = ""
            else:
                all_object_names = ",".join([obj.name for obj in collection.objects])
                
            for obj in objects:
                for direction in DIRECTIONS:
                    prop_name = f"wfc_{direction.lower()}"
                    if not props.overwrite_constraints and prop_name in obj:
                        self.report({'INFO'}, f"Property {prop_name} of {obj.name} already initialized.")
                    else:
                        obj[prop_name]=all_object_names 
            
            self.report({'INFO'}, "Collection objects initialized.")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}
    
class WFC3DPanel(bpy.types.Panel):
    """User interface for WFC 3D Add-On"""
    bl_label = "WFC 3D Generator"
    bl_idname = "VIEW3D_PT_wfc_3d"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Create'

    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        
        layout.label(text="Source Collection")
        layout.prop(props, "collection_name")
        layout.label(text="Grid Size (width/depth/height)")
        layout.prop(props, "grid_size")
        layout.prop(props, "spacing")
        
        layout.prop(context.scene,"use_constraints")
        layout.prop(props, "use_constraints") 
        box = layout.box()
        box.enabled = context.scene.wfc_props.use_constraints
        box.prop(props, "empty_constraints")
        box.prop(props, "overwrite_constraints")
        box.operator("object.wfc_3d_init_collection")
        box.label(text="All source objects will get custom properties.", icon="INFO_LARGE")
        
        layout.separator()
        layout.label(text="Target Collection")
        layout.prop(props, "target_collection")
        layout.prop(props, "link_objects")
        layout.prop(props, "remove_target_collection")
        layout.prop(props, "seed")
       
        layout.separator(type="LINE", factor=0.2)
        
        if context.scene.wfc_props.remove_target_collection:
            layout.label(text="Target collection will be removed!", icon="WARNING_LARGE")
        layout.operator("object.wfc_3d_generate")

def register():
    bpy.utils.register_class(WFC3DProperties)
    bpy.utils.register_class(OBJECT_OT_WFC3DGenerate)
    bpy.utils.register_class(OBJECT_OT_WFC3DCollectionInit)
    bpy.utils.register_class(WFC3DPanel)
    
    bpy.types.Scene.wfc_props = bpy.props.PointerProperty(type=WFC3DProperties)

def unregister():
    bpy.utils.unregister_class(WFC3DProperties)
    bpy.utils.unregister_class(OBJECT_OT_WFC3DGenerate)
    bpy.utils.unregister_class(OBJECT_OT_WFC3DCollectionInit)
    bpy.utils.unregister_class(WFC3DPanel)
    del bpy.types.Scene.wfc_props

if __name__ == "__main__":
    register()