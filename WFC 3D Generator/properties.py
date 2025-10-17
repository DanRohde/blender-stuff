import bpy

from .constants import PROP_DEFAULTS, DIRECTIONS, TRANSFORMATION_CONSTRAINTS, FREQUENCY_CONSTRAINTS


def handle_update_collection(self, context):
    props = context.scene.wfc_props
    if props.collection_obj is None:
        return
    props.obj_list.clear()
    props.neighbor_list.clear()
    for obj in props.collection_obj.objects:
        item = props.obj_list.add()
        item.name = obj.name
        item = props.neighbor_list.add()
        item.name = obj.name
        item.value = obj.name
    for obj in props.collection_obj.children:
        item = props.obj_list.add()
        item.name = obj.name
        item = props.neighbor_list.add()
        item.name = obj.name 
        item.value = obj.name

def handle_edit_neighbor_constraint_update(self, context):
    props = context.scene.wfc_props
    if props.edit_neighbor_constraint == "_NONE_":
        return
    sel_obj_list = [ item.name for item in props.obj_list if item.selected ]
    if len(sel_obj_list) == 0:
        return
    obj_name = sel_obj_list[0]
    if obj_name in props.collection_obj.objects:
        obj = props.collection_obj.objects[obj_name]
    elif obj_name in props.collection_obj.children:
        obj = props.collection_obj.children[obj_name].objects[0]
    
    
    if props.edit_neighbor_constraint in obj:
        vals = obj[props.edit_neighbor_constraint].split(",")
        props.no_neighbor_allowed = '-' in vals
        
        for item in props.neighbor_list:
            item.selected = item.value in vals
    else:
        props.no_neighbor_allowed = False
        for item in props.neighbor_list:
            item.selected = False            
        
def update_constraint_properties(self, context):
    
    props = bpy.context.scene.wfc_props
    collection = props.collection_obj

    selected = [item.name for item in props.obj_list if item.selected]
    if len(selected) == 0:
        return
    if selected[0] in collection.children:
        obj = collection.children[selected[0]].objects[0]
    else:
        obj = collection.objects[selected[0]]
    
    # reset corner properties to False
    for c in ["f","b"]:
        for nc in ["bl","br","tl","tr"]:
            props["corner_"+c+nc] = False
    # reset edge properties to False
    for e in ['fb','fl','fr','ft','bb','bl','br','bt','lt','lb','rt','rb']:
        self["edge_"+e] = False
    
    # reset face properties to False
    for f in ["front","back","left","right","top","bottom"]:
        props["face_"+f] = False
            
    props["corner_none"] = False
    props["edge_none"] = False
    props["face_none"] = False
    props["inside_none"] = False
    
    if "wfc_corners" in obj:
        for c in obj["wfc_corners"].split(","):
            props["corner_"+c] = True
        if obj["wfc_corners"] == "-":
            props["corner_none"] = True
    
    if "wfc_edges" in obj:
        for c in obj["wfc_edges"].split(","):
            props["edge_"+c] = True
        if obj["wfc_edges"] == "-":
            props["edge_none"] = True
                    
    if "wfc_faces" in obj:
        for c in obj["wfc_faces"].split(","):
            props["face_"+c] = True
        if obj["wfc_faces"] == "-":
            props["face_none"] = True
         
    if "wfc_inside" in obj:
        props["inside_none"] = obj["wfc_inside"] == "-"
        
    
    for p in ["weight","probability"] + TRANSFORMATION_CONSTRAINTS + FREQUENCY_CONSTRAINTS:
        if "wfc_"+p in obj:
            props[p]=obj["wfc_"+p]
        else:
            props[p]=PROP_DEFAULTS[p]


def get_neighbor_constraint_items(_self, _context):
    
    items = [("_NONE_","Select a Neighbor Constraint","Please select a neighbor constraint"),None]
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
    selected: bpy.props.BoolProperty(default=False,update=update_constraint_properties)

class WFC3DEditPanelNeighborMultiSelItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False)
    value: bpy.props.StringProperty()
    
class WFC3DProperties(bpy.types.PropertyGroup):
    collection_obj: bpy.props.PointerProperty(name="", description="Select a collection", type=bpy.types.Collection, update=handle_update_collection)
    grid_size: bpy.props.IntVectorProperty(name="", description="Size of the 3D grid", size=3, default=(5, 5, 5), min=1, max=100,)
    spacing: bpy.props.FloatVectorProperty(name="", description="Size of a Grid Cell", subtype="TRANSLATION", default=(2.0,2.0,2.0), min=0.1,) 
    use_constraints: bpy.props.BoolProperty(name="Use Constraints", description="Use constraints", default=True,)
    target_collection: bpy.props.StringProperty(name="", description="Target collection for 3D grid", default="WFC_Generated",)
    random_start_cell: bpy.props.BoolProperty(name="Random Start Cell", description="Random start cell", default=False,)
    random_direction: bpy.props.BoolProperty(name="Random Direction", description="Random direction", default=False,)
    seed: bpy.props.IntProperty(name="Random Seed", description="Random seed", default=0,)
    link_objects: bpy.props.BoolProperty(name="Link New Objects (recommended)", description="Link new objects instead of copying them.", default=True,)
    copy_modifiers: bpy.props.BoolProperty(name="Copy Modifiers", description="Copy modifiers to linked objects.", default=False,)
    remove_target_collection: bpy.props.BoolProperty(name="Remove Target Collection", description="Remove existing target collection", default=False,)
    obj_list: bpy.props.CollectionProperty(type=WFC3DEditPanelMultiSelItem)
    obj_list_idx: bpy.props.IntProperty()
    neighbor_list: bpy.props.CollectionProperty(type=WFC3DEditPanelNeighborMultiSelItem)
    neighbor_list_idx: bpy.props.IntProperty()
    no_neighbor_allowed: bpy.props.BoolProperty(name="No Neighbor Allowed",description="No neighbor allowed", default=False,)
    
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
        update=handle_edit_neighbor_constraint_update,
    )
    auto_active_object: bpy.props.BoolProperty(name="", description="Automatically select objects selected in 3D Viewport.", default=False,)
    auto_neighbor_object: bpy.props.BoolProperty(name="", description="Automatically select objects selected in 3D Viewport.", default=False,)
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

    
    

properties = [ WFC3DEditPanelMultiSelItem, WFC3DEditPanelNeighborMultiSelItem, WFC3DProperties, ]

    