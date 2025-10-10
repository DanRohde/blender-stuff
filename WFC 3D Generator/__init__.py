# Written 2025 by Dan Rohde
# To make this add-on installable, create an extension with it:
# https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html

import bpy
from collections import deque
import random
import numpy as np

DIRECTIONS = {
    'TOP': (0, 0, 1),
    'BOTTOM': (0, 0, -1),
    'FRONT': (0, -1, 0),
    'BACK': (0, 1, 0),
    'LEFT': (-1, 0, 0),
    'RIGHT': (1, 0, 0)
}


class WFC3DProperties(bpy.types.PropertyGroup):
    collection_obj: bpy.props.PointerProperty(
        name="",
        description="Select a collection",
        type=bpy.types.Collection,
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
        name="Use Constraints",
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
                        if self.are_grid_constraints_satisfied(obj.name, constraints, (x, y, z)):
                            cell.append(obj.name)
                    
                    self.grid[x, y, z] = cell
    
        print(f"Grid: {self.grid}")
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
        if self.is_corner(pos) or self.is_edge(pos) or self.is_inside(pos):
            return False
        return (x in {0, l-1} or y in {0, w-1} or z in {0, h-1})
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
        
        random.seed(props.seed)
        self.remove_target_collection = props.remove_target_collection
        self.objects = []
        self.constraints = {}
        
        self.load_objects()
        self.load_constraints()
        
        self.grid = WFC3DGrid(self.grid_size)

    def load_objects(self):
        """Loads objects from the collection"""
        self.objects = list(self.collection.objects)
        self.objects.extend(self.collection.children)
        if not self.objects:
            raise ValueError("Collection is empty!")

    def load_constraints(self):
        """Loads constraints from custom properties"""
        for obj in self.objects:
            obj_name = obj.name
            self.constraints[obj_name] = {}
            
            if obj.name in bpy.data.collections:
                    obj = bpy.data.collections[obj.name].objects[0]
                
            if "wfc_weight" in obj and obj["wfc_weight"] != "":
                self.constraints[obj_name]["weight"] = int(obj["wfc_weight"])
            else:
                self.constraints[obj_name]["weight"] = 1

            # load grid constraints
            grid_constraints = { 'wfc_corners':'corners', 'wfc_edges':'edges', 'wfc_inside':'inside','wfc_faces' :'faces' }
            for gc in grid_constraints:
                if gc in obj and obj[gc] != "":
                    self.constraints[obj_name][grid_constraints[gc]] = obj[gc].split(",")

            count_constraints = { 'wfc_cx':'cx', 'wfc_cy':'cy', 'wfc_cz':'cz'}
            for cc in count_constraints:
                if cc in obj and obj[gc] != "":
                    self.constriants[obj_name][count_constraints[cc]] = int(obj[gc])
            
            # load neighbor constraints
            for direction in DIRECTIONS:
                prop_name = f"wfc_{direction.lower()}"
                # take first element from collection to get constraints
                if prop_name in obj:
                    if obj[prop_name] == "":
                        self.constraints[obj_name][direction] = [o.name for o in self.objects]
                    else:
                        self.constraints[obj_name][direction] = obj[prop_name].split(',')
                else:
                    # Standard: Alle Objekte erlaubt
                    self.constraints[obj.name][direction] = [o.name for o in self.objects]

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
        options = []
        for name in obj_names:
            weight = self.constraints[name]['weight']
            option = [name for _ in range(weight)]
            options.extend(option)
        return options
        
    def collapse(self, x, y, z):
        """Collapses a cell into a single state"""
        options = self.get_weighted_options(self.grid.grid[x, y, z])
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

    def execute(self, context):
        props = context.scene.wfc_props
        
        try:
            collection = props.collection_obj
            if not collection:
                raise ValueError(f"Source collection '{props.collection_obj}' not found!")
                
            generator = WFC3DGenerator(collection, props)
            generator.generate_model()
            
            self.report({'INFO'}, "WFC model successfully generated!")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}",)
            return {'CANCELLED'}
        
        
class OBJECT_OT_WFC3DCollectionInit(bpy.types.Operator):
    """Initialize object constraints"""
    bl_idname="object.wfc_3d_init_collection"
    bl_label = "Initialize Constraint Properties"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        try:
            collection = props.collection_obj
            if not collection:
                raise ValueError(f"Collection '{props.collection_obj}' not found!")
            objects = list(collection.objects)
            objects.extend(collection.children)

            if not objects:
                raise ValueError("Collection is empty!")
            
            if props.empty_constraints:
                all_object_names = ""
            else:
                all_object_names = ",".join([obj.name for obj in collection.objects])
                if len(collection.children)>0:
                    all_object_names = all_object_names + "," + ",".join([obj.name for obj in collection.children])
                
            for obj in objects:
                for constraint in ['corners','edges','faces','inside','weight']:
                    prop_name = f"wfc_{constraint}"
                    if obj.name in bpy.data.collections and len(bpy.data.collections[obj.name].objects)>0:
                        obj = bpy.data.collections[obj.name].objects[0]
                    if not props.overwrite_constraints and prop_name in obj:
                        self.report({'INFO'}, f"Property {prop_name} of {obj.name} already initialized.")
                    else:
                        obj[prop_name]=""
                for direction in DIRECTIONS:
                    prop_name = f"wfc_{direction.lower()}"
                    if obj.name in bpy.data.collections and len(bpy.data.collections[obj.name].objects)>0:
                         obj = bpy.data.collections[obj.name].objects[0]
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
        layout.prop(props, "collection_obj")
        layout.label(text="Grid Size (width/depth/height)")
        layout.prop(props, "grid_size")
        layout.prop(props, "spacing")
        
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

        if props.remove_target_collection and props.target_collection != "" and props.target_collection in bpy.data.collections:
            layout.label(text="Target collection will be removed!", icon="WARNING_LARGE")

        row = layout.row();
        row.enabled = props.collection_obj!=None and ( (len(props.collection_obj.objects)>0)or(len(props.collection_obj.children)>0) ) and props.collection_obj.name != props.target_collection
        row.operator("object.wfc_3d_generate")
        if props.collection_obj is None:
            layout.label(text="Please select a source collection.", icon="INFO_LARGE")
        if props.collection_obj is not None and props.collection_obj.name == props.target_collection:
            layout.label(text="Source and target collection should not be the same.", icon="WARNING_LARGE")
        if props.collection_obj and len(props.collection_obj.objects)==0 and len(props.collection_obj.children)==0:
            layout.label(text="Please select a non-empty source collection.", icon="INFO_LARGE")


classes = (
    WFC3DProperties,
    OBJECT_OT_WFC3DGenerate,
    OBJECT_OT_WFC3DCollectionInit,
    WFC3DPanel,
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.wfc_props = bpy.props.PointerProperty(type=WFC3DProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.wfc_props
    del bpy.types.Scene.wfc_picker

if __name__ == "__main__":
    register()