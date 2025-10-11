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
def get_object_enum_items(self, context):
    items = [('_none_','Select an object','Select an object'),None]
    collection = self.collection_obj
    if collection and (len(collection.objects)>0 or len(collection.children)>0):
        for obj in collection.objects:
            items.append((obj.name, obj.name, f"Objekt: {obj.name}" ))
        if len(collection.children)>0:
            items.append(None)
        for obj in collection.children:
            items.append((obj.name, obj.name, f"Collection: {obj.name}"))
    else:
        items.append(("NONE", "No Objects", ""))
        
    return items

def get_object_edit_enum_items(self, context):
    items = [('_none_','Select an object','Select an object'),None]
    collection = self.collection_obj
    if collection and (len(collection.objects)>0 or len(collection.children)>0):
        for obj in collection.objects:
            items.append((obj.name, obj.name, f"Objekt: {obj.name}" ))
        if len(collection.children)>0:
            items.append(None)
        for obj in collection.children:
            items.append((obj.name, obj.name, f"Collection: {obj.name}"))
        items.append(None)
        items.append(('-','No Neighbor allowed','No neighbor allowed'))
    else:
        items.append(("NONE", "No Objects", ""))
        
    return items

def update_constraint_properties(self, context):
    collection = self.collection_obj
    obj_name = self.edit_object
    
    if obj_name in collection.children:
        obj = collection.children[obj_name].objects[0]
    else:
        obj = collection.objects[obj_name]
    
    
    # reset corner properties to False
    for c in ["f","b"]:
        for nc in ["bl","br","tl","tr"]:
            self["corner_"+c+nc] = False
    # reset edge properties to False
    for e in ['fb','fl','fr','ft','bb','bl','br','bt','lt','lb','rt','rb']:
        self["edge_"+e] = False
    
    # reset face properties to False
    for f in ["front","back","left","right","top","bottom"]:
        self["face_"+f] = False
    
    # reset rotation properties
    for i in ["x","y","z"]:
        self["rotation_"+i] = False
    
    self["rotation_d"] = (0,0,0)
    self["rotation_s"] = (0,0,0)
        
    self["inside_none"] = False
    
    if "wfc_corners" in obj:
        for c in obj["wfc_corners"].split(","):
            self["corner_"+c] = True
        if obj["wfc_corners"] == "-":
            self["corner_none"] = True
    
    if "wfc_edges" in obj:
        for c in obj["wfc_edges"].split(","):
            self["edge_"+c] = True
        if obj["wfc_edges"] == "-":
            self["edge_none"] = True
                    
    if "wfc_faces" in obj:
        for c in obj["wfc_faces"].split(","):
            self["face_"+c] = True
        if obj["wfc_faces"] == "-":
            self["face_none"] = True
         
    if "wfc_inside" in obj:
        self["inside_none"] = obj["wfc_inside"] == "-"
         
         
    if "wfc_weight" in obj and obj["wfc_weight"]!="":
        self["weight"] = int(obj["wfc_weight"])
    else:
        self["weight"] = 1
    
    if "wfc_rotation" in obj and obj["wfc_rotation"] != "":
        r= obj["wfc_rotation"].split(",")
        self["rotation_x"]="x" in r
        self["rotation_y"]="y" in r
        self["rotation_z"]="z" in r
    if "wfc_rotation_d" in obj:
        self["rotation_d"] = obj["wfc_rotation_d"]
    if "wfc_rotation_s" in obj:
        self["rotation_s"] = obj["wfc_rotation_s"]
    
    prop_defaults = {"scale_min":(1,1,1), "scale_max":(1,1,1), "translation_min":(0,0,0),"translation_max":(0,0,0)}
    for p in ["scale_min","scale_max","translation_min","translation_max"]:
        if "wfc_"+p in obj:
            self[p]=obj["wfc_"+p]
        else:
            self[p]=prop_defaults[p]

    
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
    spacing: bpy.props.FloatVectorProperty(
        name="",
        description="Size of a Grid Cell",
        subtype="TRANSLATION",
        default=(2.0,2.0,2.0),
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
    
    edit_object: bpy.props.EnumProperty(
        name="",
        description="Select an object",
        items=get_object_enum_items,
        update=update_constraint_properties
    )
    
    edit_constraints: bpy.props.EnumProperty(
        name="",
        description = "Select constraint type",
        items=[("_none_","Select a Constraint Type","Select a constraint type"),("neighbor","Neighbor Constraints","Neighbor constraints"),\
               ("grid","Grid Constraints","Grid constraints"),("weight","Weight Constraints", "Weight constraints"),\
               ("rotation","Rotation Constraints", "Rotation constraints"), ("geometry","Geometry Constraints", "Geometry constraints")],
        update=update_constraint_properties
    )
    edit_neighbor_constraint: bpy.props.EnumProperty(
        name="",
        description="Select a Neighbor Constraint",
        items=[("_none_","Select a Constraint","Please select a neighbor constraint"),('wfc_left','Left','Left Neighbor'),('wfc_right','Right','Right Neighbor'),\
               ('wfc_top','Top','Top Neighbor'),('wfc_bottom','Bottom','Bottom Neighbor'),('wfc_front','Front','Front Neighbor'),('wfc_back','Back','Back Neighbor'),],
    )
    select_neighbor: bpy.props.EnumProperty(
        name="Select neighbor",
        description="Select a Neighbor",
        items=get_object_edit_enum_items,
    )
    corner_fbl: bpy.props.BoolProperty( name="fbl", description="Front Bottom Left")
    corner_fbr: bpy.props.BoolProperty( name="fbr", description="Front Bottom Right")
    corner_ftl: bpy.props.BoolProperty( name="ftl", description="Front Top Left")
    corner_ftr: bpy.props.BoolProperty( name="ftr", description="Front Top Right")
    corner_bbl: bpy.props.BoolProperty( name="bbl", description="Back Bottom Left")
    corner_bbr: bpy.props.BoolProperty( name="bbr", description="Back Bottom Right")
    corner_btl: bpy.props.BoolProperty( name="btl", description="Back Top Left")
    corner_btr: bpy.props.BoolProperty( name="btr", description="Back Top Right")
    corner_none: bpy.props.BoolProperty(name="-", description="Forbidden")
    edge_fb: bpy.props.BoolProperty(name="fb", description="Front Buttom")
    edge_fl: bpy.props.BoolProperty(name="fl", description="Front Left")
    edge_fr: bpy.props.BoolProperty(name="fr", description="Front Right")
    edge_ft: bpy.props.BoolProperty(name="ft", description="Front Top")
    edge_bb: bpy.props.BoolProperty(name="bb", description="Back Bottom")
    edge_bl: bpy.props.BoolProperty(name="bl", description="Back Left")
    edge_br: bpy.props.BoolProperty(name="br", description="Back Right")
    edge_bt: bpy.props.BoolProperty(name="bt", description="Back Top")
    edge_lt: bpy.props.BoolProperty(name="lt", description="Left Top")
    edge_lb: bpy.props.BoolProperty(name="lb", description="Left Buttom")
    edge_rt: bpy.props.BoolProperty(name="rt", description="Right Top")
    edge_rb: bpy.props.BoolProperty(name="rb", description="Right Buttom")
    edge_none:bpy.props.BoolProperty(name="-", description="Edge Forbidden")
    face_front: bpy.props.BoolProperty(name="front", description="Front")
    face_back: bpy.props.BoolProperty(name="back", description="Back")
    face_left: bpy.props.BoolProperty(name="left", description="Left")
    face_right: bpy.props.BoolProperty(name="right", description="Right")
    face_top: bpy.props.BoolProperty(name="top", description="Top")
    face_bottom: bpy.props.BoolProperty(name="bottom", description="Bottom")
    face_none: bpy.props.BoolProperty(name="-", description="Faces Forbidden")
    inside_none: bpy.props.BoolProperty(name="-", description="Inside Forbidden")
    weight: bpy.props.IntProperty(name="Weight", description="Weight Property", default=1, min=0)
    rotation_x: bpy.props.BoolProperty(name="x", default=False, description="allow X rotation")
    rotation_y: bpy.props.BoolProperty(name="y", default=False, description="allow Y rotation")
    rotation_z: bpy.props.BoolProperty(name="z", default=False, description="allow Y rotation")
    rotation_d : bpy.props.FloatVectorProperty(name="Degrees max", description="Degrees max", default=(0,0,0), subtype="EULER")
    rotation_s : bpy.props.FloatVectorProperty(name="Degrees steps", description="Degree Steps", default=(0,0,0), subtype="EULER")
    scale_min : bpy.props.FloatVectorProperty(name="Scale min", description="Scale minimum", default=(1,1,1))
    scale_max : bpy.props.FloatVectorProperty(name="Scale max", description="Scale maximum", default=(1,1,1))
    translation_min : bpy.props.FloatVectorProperty(name="Translation min", description="Translation minimum", default=(0,0,0), subtype="TRANSLATION")
    translation_max : bpy.props.FloatVectorProperty(name="Translation max", description="Translation maximum", default=(0,0,0), subtype="TRANSLATION")
    
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
        
        random.seed(props.seed)
        self.remove_target_collection = props.remove_target_collection
        self.objects = []
        self.constraints = None
        self.load_objects()

        if self.use_constraints:
            self.constraints = {}
            self.count_constraints = { "cx" : [ (-1,0,0),(1,0,0)], "cy" : [(0,-1,0),(0,1,0)], "cz" : [(0,0,-1),(0,0,1)] }
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
            
            # load rotation constraints
            if "wfc_rotation" in obj:
                self.constraints[obj_name]["rotation"] = obj["wfc_rotation"].split(",")
            else:
                self.constraints[obj_name]["rotation"] = None
            if "wfc_rotation_d" in obj:
                self.constraints[obj_name]["rotation_d"] = obj["wfc_rotation_d"]
            else:
                self.constraints[obj_name]["rotation_d"] = None
            if "wfc_rotation_s" in obj:
                self.constraints[obj_name]["rotation_s"] = obj["wfc_rotation_s"]
            else:
                self.constraints[obj_name]["rotation_s"] = None
            
            
            for c in ["scale_min","scale_max","translation_min","translation_max"]:
                if "wfc_"+c in obj:
                    self.constraints[obj_name][c] = obj["wfc_"+c]
                else:
                    self.constraints[obj_name][c] = None
                
            count_constraints = { 'wfc_cx':'cx', 'wfc_cy':'cy', 'wfc_cz':'cz', 'wfc_cg' : 'cg' }
            for cc in count_constraints:
                if cc in obj and obj[cc] != "":
                    self.constraints[obj_name][count_constraints[cc]] = int(obj[cc])
            
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
                        else:
                            new_obj = original_obj.copy()
                            new_obj.data = original_obj.data.copy()
                        
                        nx = x * self.spacing[0]
                        ny = y * self.spacing[1]
                        nz = z * self.spacing[2]
                        
                        if self.use_constraints:
                            if self.constraints[obj_name]["translation_min"] and self.constraints[obj_name]["translation_max"]:
                                tmin = self.constraints[obj_name]["translation_min"]
                                tmax = self.constraints[obj_name]["translation_max"]
                                nx+= tmin[0] + random.random()*(tmax[0]-tmin[0])
                                ny+= tmin[1] + random.random()*(tmax[1]-tmin[1])
                                nz+= tmin[2] + random.random()*(tmax[2]-tmin[2])
                            if self.constraints[obj_name]["scale_min"] and self.constraints[obj_name]["scale_max"]:
                                smin = self.constraints[obj_name]["scale_min"]
                                smax = self.constraints[obj_name]["scale_max"]
                                new_obj.scale.x = smin[0] + random.random()*(smax[0]-smin[0])
                                new_obj.scale.y = smin[1] + random.random()*(smax[1]-smin[1])
                                new_obj.scale.z = smin[2] + random.random()*(smax[2]-smin[2])
                            if self.constraints[obj_name]["rotation"]:
                                a = self.constraints[obj_name]["rotation"]
                                d = self.constraints[obj_name]["rotation_d"]
                                s = self.constraints[obj_name]["rotation_s"]
                                if d and s and a!="":
                                    axisparam=["X","Y","Z"]
                                    for i in range(len(axisparam)):
                                        if axisparam[i].lower() in a:
                                            if s[i]!=0 and d[i]!=0:
                                                v = [ m for m in np.arange(0,d[i],s[i]) ]
                                                angleidx = random.randrange(0,len(v)) 
                                                if v[angleidx]!=0:
                                                    new_obj.rotation_euler.rotate_axis(axisparam[i], v[angleidx])
                        
                        new_obj.location = (nx, ny, nz)        
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

    
class WFC3DGeneratePanel(bpy.types.Panel):
    """User interface for WFC 3D Add-On"""
    bl_label = "WFC 3D Generator"
    bl_idname = "VIEW3D_PT_wfc_3d"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Gen'

    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        
        layout.label(text="Source Collection")
        layout.prop(props, "collection_obj")
        layout.label(text="Grid Size (width/depth/height)")
        layout.prop(props, "grid_size")
        layout.label(text="Grid Cell Space")
        layout.prop(props, "spacing")
        
        layout.prop(props, "use_constraints")
        
        layout.separator()
        layout.label(text="Target Collection")
        layout.prop(props, "target_collection")
        layout.prop(props, "link_objects")
        layout.prop(props, "remove_target_collection")
        layout.prop(props, "seed")

        layout.separator(type="LINE", factor=0.2)

        if props.remove_target_collection and props.target_collection != "" and props.target_collection in bpy.data.collections:
            layout.box().label(text="Target collection will be removed!", icon="WARNING_LARGE")
            

        row = layout.row();
        row.enabled = props.collection_obj!=None and ( (len(props.collection_obj.objects)>0)or(len(props.collection_obj.children)>0) ) and props.collection_obj.name != props.target_collection
        row.operator("object.wfc_3d_generate")
        if props.collection_obj is None:
            layout.label(text="Please select a source collection.", icon="INFO_LARGE")
        if props.collection_obj is not None and props.collection_obj.name == props.target_collection:
            layout.label(text="Source and target collection should not be the same.", icon="WARNING_LARGE")
        if props.collection_obj and len(props.collection_obj.objects)==0 and len(props.collection_obj.children)==0:
            layout.label(text="Please select a non-empty source collection.", icon="INFO_LARGE")




class COLLECTION_OT_WFC3DSelectDropdownObject(bpy.types.Operator):
    """Activates Object"""
    bl_idname = "collection.wfc_select_dropdown_object"
    bl_label = "Select"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.wfc_props
        collection = props.collection_obj
        obj_name = props.edit_object

        if not collection or obj_name == "NONE":
            self.report({'WARNING'}, "Empty Collection")
            return {'CANCELLED'}

        if obj_name in collection.children and len(collection.children[obj_name].objects)>0:
            obj = collection.children[obj_name].objects[0]
        else:
            obj = collection.objects[obj_name]
        
        if not obj:
            self.report({'WARNING'}, "Object not found")
            return {'CANCELLED'}

    
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            for area in context.window.screen.areas:
                if area.type == 'PROPERTIES':
                    for space in area.spaces:
                        if space.type == 'PROPERTIES':
                            space.context = 'OBJECT'
                            break
        except Exception as e:
            self.report({'WARNING'}, f"Error: {str(e)}")

        self.report({'INFO'}, f"Activated Objekt: {obj.name}")
        return {'FINISHED'}

class WFC3DEditPanel(bpy.types.Panel):
    """User interface for WFC 3D Add-On"""
    bl_label = "WFC 3D Constraint Editor"
    bl_idname = "VIEW3D_PT_wfc_3d_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Edit'

    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        layout.label(text="Source Collection")
        layout.prop(props, "collection_obj")
        col = layout.column(align=True)
        if props.collection_obj:
            row = col.row()
            row.label(text="Select an Object")
            row.prop(props, "edit_object")
            newrow = row.row()
            newrow.operator("collection.wfc_select_dropdown_object", icon='RESTRICT_SELECT_OFF')
            newrow.enabled = False
            if props.edit_object and props.edit_object != '_none_':
                newrow.enabled = True

                if props.edit_object in props.collection_obj.children:
                    obj=props.collection_obj.children[props.edit_object].objects[0]
                else:
                    obj=props.collection_obj.objects[props.edit_object]
                    
                row=col.row();
                row.box().prop(props,"edit_constraints")
                if (props.edit_constraints == "neighbor"):
                    box=col.box()
                    box.label(text="Neighbor Constraints")
                    row = box.row()
                    row.prop(props,"edit_neighbor_constraint")
                    newrow = row.row()
                    newrow.operator("object.wfc_clear_constraint")
                    newrow.enabled = props.edit_neighbor_constraint in obj;
                    
                    if (props.edit_neighbor_constraint and props.edit_neighbor_constraint !="_none_"):
                        if props.edit_neighbor_constraint in obj:  
                            box.label(text="Neighbors: "+obj[props.edit_neighbor_constraint])
                        else:
                            box.label(text="Neighbors:")
                        box.prop(props,"select_neighbor")
                        row=box.row()
                        if (props.select_neighbor and props.select_neighbor != '_none_'):
                            row.operator("object.wfc_add_constraint", icon='ADD')
                            row.operator("object.wfc_remove_constraint", icon='REMOVE')
                if (props.edit_constraints == "grid"):    
                    box=col.box()
                    box.label(text="Grid Constraints")
                    newbox = box.box()
                    newrow = newbox.row()
                    newrow.label(text="Corners")
                    newrow.prop(props, "corner_none")    
                    if not props.corner_none:
                        row = newbox.row()
                        for c in ['fbl','fbr','ftl','ftr']:
                            row.prop(props,"corner_"+c)
                            
                        row = newbox.row()
                        for c in ['bbl','bbr','btl','btr']:
                            row.prop(props,"corner_"+c)
                    
                    newbox = box.box()
                    newrow = newbox.row()
                    newrow.label(text="Edges")
                    newrow.prop(props,"edge_none")
                    if not props.edge_none:
                        for p in ['f','b']:
                            row = newbox.row()
                            for c in ['b','l','t','r']:
                                row.prop(props,"edge_"+p+c)
                        row = newbox.row()
                        for p in ['lb','lt','rb','rt']:
                            row.prop(props,"edge_"+p)
                    
                    newbox = box.box()
                    newrow = newbox.row()
                    newrow.label(text="Faces")
                    newrow.prop(props, "face_none")
                    if not props.face_none:
                        row = newbox.row()
                        for f in ['front','left','top']:
                            row.prop(props, "face_"+f)
                        row = newbox.row()
                        for f in ['back','right','bottom']:
                            row.prop(props,"face_"+f)
                        
                    
                    newbox = box.box()
                    newrow = newbox.row()
                    newrow.label(text="Inside")
                    newrow.prop(props,"inside_none")
                    
                    
                    box.operator("object.wfc_update_grid_constraints",icon='FILE_REFRESH')
                if (props.edit_constraints == "weight"):
                    box=col.box()
                    box.label(text="Weight Constraints")
                    newbox = box.box()
                    newbox.prop(props, "weight")
                    
                    box.operator("object.wfc_update_weight_constraints", icon='FILE_REFRESH')    
                if (props.edit_constraints == "rotation"):
                    box=col.box()
                    box.label(text="Rotation Constraints")
                    newrow=box.row()
                    newrow.label(text="Allow:")
                    newrow.prop(props, "rotation_x")
                    newrow.prop(props, "rotation_y")
                    newrow.prop(props, "rotation_z")
                    box.row().prop(props,"rotation_d")
                    box.row().prop(props,"rotation_s")
                    
                    box.operator('object.wfc_update_rotation_constraints',icon='FILE_REFRESH')
                if (props.edit_constraints == "geometry"):
                    box=col.box()
                    box.label(text="Geometry Constraints")
                    box.row().prop(props,"scale_min")
                    box.row().prop(props,"scale_max")
                    box.row().prop(props,"translation_min")
                    box.row().prop(props,"translation_max")
                    box.operator('object.wfc_update_geometry_constraints',icon='FILE_REFRESH')
        else:
            layout.label(text="Choose a Source Collection", icon='INFO')

        
class COLLECTION_OT_WFC3DAdd_Neighbor_Constraint(bpy.types.Operator):
    bl_idname = "object.wfc_add_constraint"
    bl_label = "Add Neighbor"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props= context.scene.wfc_props
        obj_name = props.edit_object
        prop_name = props.edit_neighbor_constraint
        neighbor = props.select_neighbor
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name][0]
        else:
            obj = bpy.data.objects[obj_name]
        if prop_name in obj:
            if obj[prop_name] == "":
                l = []
            else:
                if obj[prop_name] == "-":
                    l = []
                else: 
                    l = obj[prop_name].split(",")
            if neighbor not in l:
                if neighbor == '-':
                    l = []
                l.append(neighbor)
                obj[prop_name]=",".join(l)
                self.report({'INFO'}, f"Neighbor {neighbor} added to {prop_name} of object {obj_name}")  
            else:
                self.report({'WARNING'}, f"Neighbor {neighbor} is already in {prop_name} of object {obj_name}")
        else:
            obj[prop_name] = neighbor
        return {'FINISHED'}

        
class COLLECTION_OT_WFC3DRemove_Neighbor_Constraint(bpy.types.Operator):
    bl_idname = "object.wfc_remove_constraint"
    bl_label = "Remove Neighbor"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props= context.scene.wfc_props
        obj_name = props.edit_object
        prop_name = props.edit_neighbor_constraint
        neighbor = props.select_neighbor
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name][0]
        else:
            obj = bpy.data.objects[obj_name]
        
        if prop_name in obj:
            if obj[prop_name] == "" or obj[prop_name] == neighbor:
                obj[prop_name] = ""
            else:
                l = [n for n in obj[prop_name].split(",") if n != neighbor ]
                obj[prop_name] = ",".join(l)
            self.report({'INFO'}, f"Neighbor {neighbor} removed from {prop_name} of object {obj_name}")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DClear_Neighbor_Constraint(bpy.types.Operator):
    bl_idname = "object.wfc_clear_constraint"
    bl_label = "Clear"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props= context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name][0]
        else:
            obj = bpy.data.objects[obj_name]
        
        if props.edit_neighbor_constraint and props.edit_neighbor_constraint in obj:
            obj[props.edit_neighbor_constraint]=""
            self.report({'INFO'}, f"{props.edit_neighbor_constraint} cleared for object: {obj_name}")

        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Grid_Constraints(bpy.types.Operator):
    bl_idname = "object.wfc_update_grid_constraints"
    bl_label = "Update Grid Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def _get_new_prop_val(self, props, prop_name, values):
        newval = []
        if prop_name+"_none" in props and props[prop_name+"_none"]:
            newval.append("-")
        else:
            for v in values:
                if props[prop_name+"_"+v]:
                    newval.append(v)
        return ",".join(newval)
        
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
        
        obj["wfc_corners"]= self._get_new_prop_val(props, "corner",['fbl','fbr','ftl','ftr','bbl','bbr','btl','btr'])
        obj["wfc_edges"] = self._get_new_prop_val(props, "edge",['fb','fl','fr','ft','bb','bl','br','bt','lb','lt','rb','rt'])
        obj["wfc_faces"] = self._get_new_prop_val(props, "face",['front','back','top','bottom','left','right'])
        if props["inside_none"]:
            obj["wfc_inside"] = "-"
        else:
            obj["wfc_inside"] = ""
        
        self.report({'INFO'}, f"Grid constraints of object {obj_name} updated.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Weight_Constraints(bpy.types.Operator):
    bl_idname = "object.wfc_update_weight_constraints"
    bl_label = "Update Weight Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
        
        obj["wfc_weight"] = props.weight;
        self.report({'INFO'}, f"Weight constraints of object {obj_name} updated to {props.weight}.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Rotation_Constraints(bpy.types.Operator):
    bl_idname = "object.wfc_update_rotation_constraints"
    bl_label = "Update Rotation Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
        
        newval=[]
        for n in ["x","y","z"]:
            if props["rotation_"+n]:
                newval.append(n)
        obj["wfc_rotation"] = ",".join(newval)
        
        obj["wfc_rotation_d"] = props["rotation_d"]
        obj["wfc_rotation_s"] = props["rotation_s"]
        
        self.report({'INFO'}, f"Rotation constraints of object {obj_name} updated.")  

        return {'FINISHED'}

class COLLECTION_OT_WFC3DUpdate_Geometry_Constraints(bpy.types.Operator):
    bl_idname = "object.wfc_update_geometry_constraints"
    bl_label = "Update Geometry Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
        
        prop_defaults = {"scale_min" : (1.0,1.0,1.0), "scale_max" : (1.0,1.0,1.0), "translation_min" : (0.0,0.0,0.0), "translation_max" :(0.0,0.0,0.0)}
        for c in prop_defaults:
            if c in props:
                obj["wfc_"+c] = props[c]
            else:
                obj["wfc" +c] = prop_defaults[c]
         
        self.report({'INFO'}, f"Geometry constraints of object {obj_name} updated.")  

        return {'FINISHED'}
classes = (
    WFC3DProperties,
    OBJECT_OT_WFC3DGenerate,
    COLLECTION_OT_WFC3DSelectDropdownObject,
    COLLECTION_OT_WFC3DAdd_Neighbor_Constraint,
    COLLECTION_OT_WFC3DRemove_Neighbor_Constraint,
    COLLECTION_OT_WFC3DClear_Neighbor_Constraint,
    COLLECTION_OT_WFC3DUpdate_Grid_Constraints,
    COLLECTION_OT_WFC3DUpdate_Weight_Constraints,
    COLLECTION_OT_WFC3DUpdate_Rotation_Constraints,
    COLLECTION_OT_WFC3DUpdate_Geometry_Constraints,
    WFC3DEditPanel,
    WFC3DGeneratePanel,
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.wfc_props = bpy.props.PointerProperty(type=WFC3DProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.wfc_props

if __name__ == "__main__":
    register()