import bpy

from .constants import PROP_DEFAULTS, DIRECTIONS, TRANSFORMATION_CONSTRAINTS, FREQUENCY_CONSTRAINTS

def get_object_enum_items(self, context):
    items = [('_none_','Select an object','Select an object'),None]
    collection = self.collection_obj
    if collection and (len(collection.objects)>0 or len(collection.children)>0):
        for obj in collection.objects:
            items.append((obj.name, obj.name, f"Object: {obj.name}" ))
        if len(collection.children)>0:
            items.append(None)
        for obj in collection.children:
            items.append((obj.name, obj.name, f"Collection: {obj.name}"))
        items.append(("_ALL_","-- All Objects --","All objects"))
        items.append(("_LIST_","-- Select Object List --","Select object list"))
    else:
        items.append(("NONE", "No Objects", ""))
        
    return items

def get_object_edit_enum_items(self, context):
    items = [('_none_','Select a Neighbor','Select an object'),None]
    collection = self.collection_obj
    if collection and (len(collection.objects)>0 or len(collection.children)>0):
        for obj in collection.objects:
            items.append((obj.name, obj.name, f"Object: {obj.name}" ))
        if len(collection.children)>0:
            items.append(None)
        for obj in collection.children:
            items.append((obj.name, obj.name, f"Collection: {obj.name}"))
        items.append(None)
        items.append(('-','No Neighbor allowed','No neighbor allowed'))
    else:
        items.append(("NONE", "No Objects", ""))
        
    return items

def handle_update_collection(self, context):
    props = context.scene.wfc_props
    if props.collection_obj is None:
        return
    props.obj_list.clear()
    for obj in props.collection_obj.objects:
        item = props.obj_list.add()
        item.name = obj.name
    for obj in props.collection_obj.children:
        item = props.obj_list.add()
        item.name = obj.name


def update_constraint_properties(self, context):
    collection = self.collection_obj
    obj_name = self.edit_object
    
    if obj_name == '_LIST_':
        selected = [item.name for item in self.obj_list if item.selected]
        if len(selected) == 0:
            return
        if selected[0] in collection.children:
            obj = collection.children[selected[0]].objects[0]
        else:
            obj = collection.objects[selected[0]]
    elif obj_name == '_ALL_':
        obj = collection.objects[0]
    else:
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
            
    self["corner_none"] = False
    self["edge_none"] = False
    self["face_none"] = False
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
        
    
    for p in ["weight","probability"] + TRANSFORMATION_CONSTRAINTS + FREQUENCY_CONSTRAINTS:
        if "wfc_"+p in obj:
            self[p]=obj["wfc_"+p]
        else:
            self[p]=PROP_DEFAULTS[p]


def get_neighbor_constraint_items(_self, _context):
    
    items = [("_none_","Select a Neighbor Constraint","Please select a neighbor constraint"),None]
    translate = { 'TOP': 'top face', 'BOTTOM' : 'bottom face', 'LEFT' : 'left face', 'RIGHT': 'right face', 'FRONT' : 'front face', 'BACK' : 'back face',
                 'FBL':'front bottom left corner', 'FBR' : 'front bottom right corner', 'FTL' : 'front top left corner', 'FTR' : 'front top right corner',
                 'BBL':'back bottom left corner', 'BBR' : 'back bottom right corner', 'BTL' : 'back top left corner', 'BTR' : 'back top right corner', 
                 'FL':'front left edge', 'FR': 'front right edge', 'FB' : 'front bottom edge', 'FT' : 'front top edge',
                 'BL':'back left edge', 'BR': 'back right edge', 'BB' : 'back bottom edge', 'BT' : 'back top edge',
                 'LT':'left top edge', 'LB' : 'left bottom edge', 'RT' : 'right top edge', 'RB' : 'right bottom edge',
                 }
    ls = ""
    for d in DIRECTIONS:
        label = d.lower()
        if d.find("_")>-1:
            s, n = d.split("_",1)
            if ls != s :
                ls = s 
                items.append(None)
            if n in translate:
                label = translate[n]
        else:
            if d in translate:
                label = translate[d] 
            
        items.append(('wfc_'+d.lower(),label,label+" neighbor"))
    return items

class WFC3DEditPanelMultiSelItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False)
    
class WFC3DProperties(bpy.types.PropertyGroup):
    collection_obj: bpy.props.PointerProperty(name="", description="Select a collection", type=bpy.types.Collection, update=handle_update_collection)
    grid_size: bpy.props.IntVectorProperty(name="", description="Size of the 3D grid", size=3, default=(5, 5, 5), min=1, max=100,)
    spacing: bpy.props.FloatVectorProperty(name="", description="Size of a Grid Cell", subtype="TRANSLATION", default=(2.0,2.0,2.0), min=0.1,) 
    use_constraints: bpy.props.BoolProperty(name="Use Constraints", description="Use constraints", default=True,)
    target_collection: bpy.props.StringProperty(name="", description="Target collection for 3D grid", default="WFC_Generated",)
    random_start_cell: bpy.props.BoolProperty(name="Random Start Cell", description="Random start cell", default=True,)
    seed: bpy.props.IntProperty(name="Random Seed", description="Random seed", default=0,)
    link_objects: bpy.props.BoolProperty(name="Link New Objects (recommended)", description="Link new objects instead of copying them.", default=True,)
    copy_modifiers: bpy.props.BoolProperty(name="Copy Modifiers", description="Copy modifiers to linked objects.", default=False,)
    remove_target_collection: bpy.props.BoolProperty(name="Remove Target Collection", description="Remove existing target collection", default=False,)
    obj_list: bpy.props.CollectionProperty(type=WFC3DEditPanelMultiSelItem)
    obj_list_idx: bpy.props.IntProperty()
    edit_object: bpy.props.EnumProperty(name="", description="Select an object", items=get_object_enum_items, update=update_constraint_properties,)
    edit_constraints: bpy.props.EnumProperty(
        name="", description = "Select constraint type",
        items=[("_none_","Select a Constraint Type","Select a constraint type"),("neighbor","Neighbor Constraints","Neighbor constraints"),
               ("grid","Grid Constraints","Grid constraints"),("probability","Probability Constraints", "Probability constraints"),
               ("transformation","Transformation Constraints", "Transformation constraints"), 
               ('frequency',"Frequency Constraints","Frequency constraints")
               #("symmetry","Symmetry Constraints","Symmetry constraints"),
               ],
        update=update_constraint_properties,
    )
    edit_neighbor_constraint: bpy.props.EnumProperty(
        name="", description="Select a Neighbor Constraint",
        items=get_neighbor_constraint_items,
    )
    auto_active_object: bpy.props.BoolProperty(name="", description="Automatically select the active object.", default=False,)
    auto_neighbor_object: bpy.props.BoolProperty(name="", description="Automatically select the active object.", default=False,)
    select_neighbor: bpy.props.EnumProperty(name="", description="Select a Neighbor", items=get_object_edit_enum_items,)
    corner_fbl: bpy.props.BoolProperty( name="fbl", description="Front Bottom Left")
    corner_fbr: bpy.props.BoolProperty( name="fbr", description="Front Bottom Right")
    corner_ftl: bpy.props.BoolProperty( name="ftl", description="Front Top Left")
    corner_ftr: bpy.props.BoolProperty( name="ftr", description="Front Top Right")
    corner_bbl: bpy.props.BoolProperty( name="bbl", description="Back Bottom Left")
    corner_bbr: bpy.props.BoolProperty( name="bbr", description="Back Bottom Right")
    corner_btl: bpy.props.BoolProperty( name="btl", description="Back Top Left")
    corner_btr: bpy.props.BoolProperty( name="btr", description="Back Top Right")
    corner_none: bpy.props.BoolProperty(name="-", description="Forbidden")
    edge_fb: bpy.props.BoolProperty(name="fb", description="Front Bottom")
    edge_fl: bpy.props.BoolProperty(name="fl", description="Front Left")
    edge_fr: bpy.props.BoolProperty(name="fr", description="Front Right")
    edge_ft: bpy.props.BoolProperty(name="ft", description="Front Top")
    edge_bb: bpy.props.BoolProperty(name="bb", description="Back Bottom")
    edge_bl: bpy.props.BoolProperty(name="bl", description="Back Left")
    edge_br: bpy.props.BoolProperty(name="br", description="Back Right")
    edge_bt: bpy.props.BoolProperty(name="bt", description="Back Top")
    edge_lt: bpy.props.BoolProperty(name="lt", description="Left Top")
    edge_lb: bpy.props.BoolProperty(name="lb", description="Left Bottom")
    edge_rt: bpy.props.BoolProperty(name="rt", description="Right Top")
    edge_rb: bpy.props.BoolProperty(name="rb", description="Right Bottom")
    edge_none:bpy.props.BoolProperty(name="-", description="Edge Forbidden")
    face_front: bpy.props.BoolProperty(name="front", description="Front")
    face_back: bpy.props.BoolProperty(name="back", description="Back")
    face_left: bpy.props.BoolProperty(name="left", description="Left")
    face_right: bpy.props.BoolProperty(name="right", description="Right")
    face_top: bpy.props.BoolProperty(name="top", description="Top")
    face_bottom: bpy.props.BoolProperty(name="bottom", description="Bottom")
    face_none: bpy.props.BoolProperty(name="-", description="Faces Forbidden")
    inside_none: bpy.props.BoolProperty(name="-", description="Inside Forbidden")
    weight: bpy.props.IntProperty(name="Weight", description="Weight constraint", default=PROP_DEFAULTS["weight"], min=0)
    probability: bpy.props.FloatProperty(name="Probability", description="Probability constraint", default=PROP_DEFAULTS["probability"], min=0, max=1)
    rotation_min : bpy.props.FloatVectorProperty(name="Min", description="Degrees min", default=PROP_DEFAULTS["rotation_min"], subtype="EULER")
    rotation_max : bpy.props.FloatVectorProperty(name="Max", description="Degrees max", default=PROP_DEFAULTS["rotation_max"], subtype="EULER")
    rotation_steps : bpy.props.FloatVectorProperty(name="Steps", description="Degree Steps", default=PROP_DEFAULTS["rotation_steps"], subtype="EULER")
    rotation_neighbor : bpy.props.BoolVectorProperty(name="Neighbor", description="Rotate Neighbor Constraints", default=PROP_DEFAULTS["rotation_neighbor"])
    rotation_grid : bpy.props.BoolVectorProperty(name="Grid", description="Rotate Grid Constraints", default=PROP_DEFAULTS["rotation_grid"])
    scale_type: bpy.props.EnumProperty(name="",description="",items=[('_none_','No Scaling','Please select a scaling type'),('uniform','Uniform Scaling','Uniform scaling'),('non-uniform','Non-Uniform Scaling','Non-uniform scaling')])
    scale_min : bpy.props.FloatVectorProperty(name="Min", description="Scale minimum", default=PROP_DEFAULTS["scale_min"])
    scale_max : bpy.props.FloatVectorProperty(name="Max", description="Scale maximum", default=PROP_DEFAULTS["scale_max"])
    scale_steps : bpy.props.FloatVectorProperty(name="Steps", description="Scale steps", default=PROP_DEFAULTS["scale_steps"])
    scale_uni : bpy.props.FloatVectorProperty(name="Scale min/max/steps", description="Uniform scaling", default=PROP_DEFAULTS["scale_uni"])
    translation_min : bpy.props.FloatVectorProperty(name="Min", description="Translation minimum", default=PROP_DEFAULTS["translation_min"], subtype="TRANSLATION")
    translation_max : bpy.props.FloatVectorProperty(name="Max", description="Translation maximum", default=PROP_DEFAULTS["translation_max"], subtype="TRANSLATION")
    translation_steps : bpy.props.FloatVectorProperty(name="Steps", description="Translation steps", default=PROP_DEFAULTS["translation_steps"], subtype="TRANSLATION")
    freq_grid: bpy.props.IntProperty(name="Grid",description="Grid frequency max", default=PROP_DEFAULTS["freq_grid"], min=-1)
    freq_neighbor: bpy.props.IntProperty(name="Neighbor",description="Neighbor frequency max", default=PROP_DEFAULTS["freq_neighbor"], min=-1,max=26)
    freq_axes: bpy.props.IntVectorProperty(name="Axes",description="Axes frequency max", default=PROP_DEFAULTS["freq_axes"], size=3, min=-1)
    freq_any_neighbor: bpy.props.IntProperty(name="Any Neighbor",description="Any Neighbor frequency max", default=PROP_DEFAULTS["freq_any_neighbor"], min=-1,max=26)
    freq_any_axes: bpy.props.IntVectorProperty(name="Axes",description="Any Object in Axes frequency max", default=PROP_DEFAULTS["freq_any_axes"], size=3, min=-1)
    freq_neighbor_face : bpy.props.IntProperty(name="Face",description="Neighbor face frequency max", default=PROP_DEFAULTS["freq_neighbor_face"], min=-1,max=6)
    freq_neighbor_corner : bpy.props.IntProperty(name="Corner",description="Neighbor corner frequency max", default=PROP_DEFAULTS["freq_neighbor_corner"], min=-1,max=8)
    freq_neighbor_edge : bpy.props.IntProperty(name="Edge",description="Neighbor edge frequency max", default=PROP_DEFAULTS["freq_neighbor_edge"], min=-1,max=12)
    freq_any_neighbor_face : bpy.props.IntProperty(name="Face",description="Neighbor face frequency max", default=PROP_DEFAULTS["freq_any_neighbor_face"], min=-1,max=6)
    freq_any_neighbor_corner : bpy.props.IntProperty(name="Corner",description="Neighbor corner frequency max", default=PROP_DEFAULTS["freq_any_neighbor_corner"], min=-1,max=8)
    freq_any_neighbor_edge : bpy.props.IntProperty(name="Edge",description="Neighbor edge frequency max", default=PROP_DEFAULTS["freq_any_neighbor_edge"], min=-1,max=12)

    
    

properties = [ WFC3DEditPanelMultiSelItem, WFC3DProperties ]

    