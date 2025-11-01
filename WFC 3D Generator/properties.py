import bpy

from .constants import *
from .helper import auto_save, update_edit_form, handle_edit_neighbor_constraint_update, handle_conn_directions_update, get_default_empty_name


def handle_update_collection(_self, context):
    props = context.scene.wfc_props
    if props.collection_obj is None: return
    props.obj_list.clear()
    props.neighbor_list.clear()
    for obj in props.collection_obj.objects:
        if obj.name.startswith(get_default_empty_name()): continue
        item = props.obj_list.add()
        item.name = obj.name
        item = props.neighbor_list.add()
        item.name = obj.name
        item.value = obj.name
    for obj in props.collection_obj.children:
        if len(obj.objects)>0:
            item = props.obj_list.add()
            item.name = obj.name
            item = props.neighbor_list.add()
            item.name = obj.name 
            item.value = obj.name

def get_direction_list(items, prefix):
    ls = ""
    for d in DIRECTIONS:
        label = d.lower()
        if d.find("_") > -1:
            s, n = d.split("_", 1)
            if ls != s:
                ls = s
                items.append(None)
            if n in DIR_TRANSLATION:
                label = DIR_TRANSLATION[n]
        else:
            if ls!= "":
                ls = ""
                items.append(None)
            if d in DIR_TRANSLATION:
                label = DIR_TRANSLATION[d]

        items.append((prefix + d.lower(), label, label ))
    return items

def get_neighbor_constraint_items(_self, _context):
    items = [("_NONE_","Select a Neighbor Constraint","Please select a neighbor constraint"),None]
    return get_direction_list(items, "wfc_")

def get_conn_directions(_self, _context):
    items = [("_NONE_","Select a Direction","Please select a direction"),None]
    return get_direction_list(items, 'wfc_conn_')

def get_known_conn_names(_self, _context):
    props = bpy.context.scene.wfc_props
    if props.conn_directions == '_NONE_': return '_NONE_','Nothing found','No other connectors found for this (opposite) direction'
    pn = props.conn_directions
    dn = pn.split('_', 2)[2]
    odn = OPPOSITE_DIRECTIONS[dn.upper()]
    opn = 'wfc_conn_'+odn.lower()
    items = []
    opp_items = []
    dup_items = []
    for obj in props.collection_obj.objects:
        if opn in obj and not obj[opn] in dup_items:
            opp_items.append((obj[opn],obj[opn], f"Select to apply opposite connector name {obj[opn]}"))
            dup_items.append(obj[opn])
        if pn in obj and not obj[pn] in dup_items:
            items.append((obj[pn],obj[pn],f"Select to apply {obj[pn]}"))
            dup_items.append(obj[pn])
    for child in props.collection_obj.children:
        for obj in child.objects:
            if opn in obj and not obj[opn] in dup_items:
                opp_items.append((obj[opn], obj[opn], f"Select to apply opposite connector name {obj[opn]}"))
                dup_items.append(obj[opn])
            if pn in obj and not obj[pn] in dup_items:
                items.append((obj[pn], obj[pn], f"Select to apply {obj[pn]}"))
                dup_items.append(obj[pn])
    if len(items) > 0: items.sort(key=lambda i: i[0])
    if len(opp_items) > 0:
        opp_items.sort(key=lambda i: i[0])
        items.append(None)
        items.extend(opp_items)
    return items
def take_known_conn_name(_self, _context):
    props = bpy.context.scene.wfc_props
    if props.conn_known_names == '_NONE_': return
    props.conn_name = props.conn_known_names

class WFC3DEditPanelMultiSelItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False, update=update_edit_form)

class WFC3DEditPanelNeighborMultiSelItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False, update=auto_save)
    value: bpy.props.StringProperty()

class WFC3DValidatorOutputItem(bpy.types.PropertyGroup):
    severity: bpy.props.IntProperty()
    logentry: bpy.props.StringProperty()

class WFC3DProperties(bpy.types.PropertyGroup):
    collection_obj: bpy.props.PointerProperty(name="", description="Select a collection", type=bpy.types.Collection, update=handle_update_collection)
    grid_size: bpy.props.IntVectorProperty(name="", description="Size of the 3D grid", size=3, default=(5, 5, 5), min=1, max=100,)
    spacing: bpy.props.FloatVectorProperty(name="", description="Size of a Grid Cell", subtype="TRANSLATION", default=(2.0,2.0,2.0), min=0.1,)
    odd_offset: bpy.props.FloatVectorProperty(name="", description="Odd Offset", subtype="TRANSLATION", default=(0.0,0.0,0.0))
    use_constraints: bpy.props.BoolProperty(name="Use Constraints", description="Use constraints", default=True,)
    target_collection: bpy.props.StringProperty(name="", description="Target collection for 3D grid", default="WFC_Generated",)
    render_delay: bpy.props.FloatProperty(name="Render Delay", description="Render Delay in milliseconds", default=0, min=0,step=10,precision=2)
    running_delayed_renderer : bpy.props.BoolProperty(name="Running Delayed Renderer", description="Running Delayed Renderer", default=False,)
    paused_delayed_renderer: bpy.props.BoolProperty(name="Paused Delayed Renderer", description="Paused Delayed Renderer", default=False,)
    random_start_cell: bpy.props.BoolProperty(name="Random Start Cell", description="Random start cell", default=False,)
    random_direction: bpy.props.BoolProperty(name="Random Direction", description="Random direction", default=False,)
    seed: bpy.props.IntProperty(name="Random Seed", description="Random seed", default=0,)
    cherry_picking_running: bpy.props.BoolProperty(name="Cherry Picking Running", default=False,)
    link_objects: bpy.props.BoolProperty(name="Link New Objects (recommended)", description="Link new objects instead of copying them.", default=True,)
    copy_modifiers: bpy.props.BoolProperty(name="Copy Modifiers", description="Copy modifiers to linked objects.", default=False,)
    remove_target_collection: bpy.props.BoolProperty(name="Remove Target Collection", description="Remove existing target collection", default=False,)
   
    obj_list: bpy.props.CollectionProperty(type=WFC3DEditPanelMultiSelItem)
    obj_list_idx: bpy.props.IntProperty()
    edit_type: bpy.props.EnumProperty(name="", description="Select constraints type",
        items=[('objects','Object Constraints','Object constraints'),('defaults','Collection Defaults','Collection defaults')],
        update=update_edit_form,
    )
    edit_constraints: bpy.props.EnumProperty(
        name="", description = "Select constraint type",
        items=[("_none_","Select a Constraint Type","Select a constraint type"),("neighbor","Neighbor Constraints","Neighbor constraints"),
               ("grid","Grid Constraints","Grid constraints"),("region","Region Constraints","Region constraints"),("probability","Probability Constraints", "Probability constraints"),
               ("transformation","Transformation Constraints", "Transformation constraints"), 
               ('frequency',"Frequency Constraints","Frequency constraints"), ("symmetry","Symmetry Constraints","Symmetry constraints"),
               ('connector','Connector Constraints','Connector constraints'),
               ],
        update = update_edit_form
    )
    edit_neighbor_constraint: bpy.props.EnumProperty(name="", description="Select a Neighbor Constraint", items=get_neighbor_constraint_items, update=handle_edit_neighbor_constraint_update,)
    neighbor_list: bpy.props.CollectionProperty(type=WFC3DEditPanelNeighborMultiSelItem)
    neighbor_list_idx: bpy.props.IntProperty()
    no_neighbor_allowed: bpy.props.BoolProperty(name="No Neighbor Allowed", description="No neighbor allowed", default=False, update=auto_save )
    auto_active_object: bpy.props.BoolProperty(name="", description="Automatically select objects selected in 3D Viewport.", default=False,)
    auto_neighbor_object: bpy.props.BoolProperty(name="", description="Automatically select objects selected in 3D Viewport.", default=False,)
    allow_neighbor_constraint_violations: bpy.props.BoolProperty(name="Allow Neighbor Constraint Violations", description="... prevents empty grid cells", default=PROP_DEFAULTS['allow_neighbor_constraint_violations'], update=auto_save)
    corner_fbl: bpy.props.BoolProperty( name="fbl", description="Front Bottom Left", update=auto_save)
    corner_fbr: bpy.props.BoolProperty( name="fbr", description="Front Bottom Right", update=auto_save)
    corner_ftl: bpy.props.BoolProperty( name="ftl", description="Front Top Left", update=auto_save)
    corner_ftr: bpy.props.BoolProperty( name="ftr", description="Front Top Right", update=auto_save)
    corner_bbl: bpy.props.BoolProperty( name="bbl", description="Back Bottom Left", update=auto_save)
    corner_bbr: bpy.props.BoolProperty( name="bbr", description="Back Bottom Right", update=auto_save)
    corner_btl: bpy.props.BoolProperty( name="btl", description="Back Top Left", update=auto_save)
    corner_btr: bpy.props.BoolProperty( name="btr", description="Back Top Right", update=auto_save)
    corner_none: bpy.props.BoolProperty(name="-", description="Forbidden", update=auto_save)
    edge_fb: bpy.props.BoolProperty(name="fb", description="Front Bottom", update=auto_save)
    edge_fl: bpy.props.BoolProperty(name="fl", description="Front Left", update=auto_save)
    edge_fr: bpy.props.BoolProperty(name="fr", description="Front Right", update=auto_save)
    edge_ft: bpy.props.BoolProperty(name="ft", description="Front Top", update=auto_save)
    edge_bb: bpy.props.BoolProperty(name="bb", description="Back Bottom", update=auto_save)
    edge_bl: bpy.props.BoolProperty(name="bl", description="Back Left", update=auto_save)
    edge_br: bpy.props.BoolProperty(name="br", description="Back Right", update=auto_save)
    edge_bt: bpy.props.BoolProperty(name="bt", description="Back Top", update=auto_save)
    edge_lt: bpy.props.BoolProperty(name="lt", description="Left Top", update=auto_save)
    edge_lb: bpy.props.BoolProperty(name="lb", description="Left Bottom", update=auto_save)
    edge_rt: bpy.props.BoolProperty(name="rt", description="Right Top", update=auto_save)
    edge_rb: bpy.props.BoolProperty(name="rb", description="Right Bottom", update=auto_save)
    edge_none:bpy.props.BoolProperty(name="-", description="Edge Forbidden", update=auto_save)
    face_front: bpy.props.BoolProperty(name="front", description="Front", update=auto_save)
    face_back: bpy.props.BoolProperty(name="back", description="Back", update=auto_save)
    face_left: bpy.props.BoolProperty(name="left", description="Left", update=auto_save)
    face_right: bpy.props.BoolProperty(name="right", description="Right", update=auto_save)
    face_top: bpy.props.BoolProperty(name="top", description="Top", update=auto_save)
    face_bottom: bpy.props.BoolProperty(name="bottom", description="Bottom", update=auto_save)
    face_none: bpy.props.BoolProperty(name="-", description="Faces Forbidden", update=auto_save)
    inside_none: bpy.props.BoolProperty(name="-", description="Inside Forbidden", update=auto_save)
    weight: bpy.props.IntProperty(name="Weight", description="Weight constraint", default=PROP_DEFAULTS["weight"], min=0, update=auto_save)
    probability: bpy.props.FloatProperty(name="Probability", description="Probability constraint", default=PROP_DEFAULTS["probability"], min=0, max=1, update=auto_save)
    auto_weight: bpy.props.BoolProperty(name="Automatic weight determination", description="Automatic weight determination", update=auto_save)
    rotation_min : bpy.props.FloatVectorProperty(name="Min", description="Degrees min", default=PROP_DEFAULTS["rotation_min"], subtype="EULER", update=auto_save)
    rotation_max : bpy.props.FloatVectorProperty(name="Max", description="Degrees max", default=PROP_DEFAULTS["rotation_max"], subtype="EULER", update=auto_save)
    rotation_steps : bpy.props.FloatVectorProperty(name="Steps", description="Degree Steps", default=PROP_DEFAULTS["rotation_steps"], subtype="EULER", update=auto_save)
    rotation_neighbor : bpy.props.BoolVectorProperty(name="Neighbor", description="Rotate Neighbor Constraints", default=PROP_DEFAULTS["rotation_neighbor"], update=auto_save)
    rotation_grid : bpy.props.BoolVectorProperty(name="Grid", description="Rotate Grid Constraints", default=PROP_DEFAULTS["rotation_grid"], update=auto_save)
    scale_type: bpy.props.EnumProperty(name="",description="",items=[('_none_','No Scaling','Please select a scaling type'),('uniform','Uniform Scaling','Uniform scaling'),('non-uniform','Non-Uniform Scaling','Non-uniform scaling')], update=auto_save)
    scale_min : bpy.props.FloatVectorProperty(name="Min", description="Scale minimum", default=PROP_DEFAULTS["scale_min"], update=auto_save)
    scale_max : bpy.props.FloatVectorProperty(name="Max", description="Scale maximum", default=PROP_DEFAULTS["scale_max"], update=auto_save)
    scale_steps : bpy.props.FloatVectorProperty(name="Steps", description="Scale steps", default=PROP_DEFAULTS["scale_steps"], update=auto_save)
    scale_uni : bpy.props.FloatVectorProperty(name="Scale min/max/steps", description="Uniform scaling", default=PROP_DEFAULTS["scale_uni"], update=auto_save)
    translation_min : bpy.props.FloatVectorProperty(name="Min", description="Translation minimum", default=PROP_DEFAULTS["translation_min"], subtype="TRANSLATION", update=auto_save)
    translation_max : bpy.props.FloatVectorProperty(name="Max", description="Translation maximum", default=PROP_DEFAULTS["translation_max"], subtype="TRANSLATION", update=auto_save)
    translation_steps : bpy.props.FloatVectorProperty(name="Steps", description="Translation steps", default=PROP_DEFAULTS["translation_steps"], subtype="TRANSLATION", update=auto_save)
    freq_grid: bpy.props.IntProperty(name="Grid",description="Grid frequency max", default=PROP_DEFAULTS["freq_grid"], min=-1, update=auto_save)
    freq_neighbor: bpy.props.IntProperty(name="Neighbor",description="Neighbor frequency max", default=PROP_DEFAULTS["freq_neighbor"], min=-1,max=26, update=auto_save)
    freq_axes: bpy.props.IntVectorProperty(name="Axes",description="Axes frequency max", default=PROP_DEFAULTS["freq_axes"], size=3, min=-1, update=auto_save)
    freq_any_neighbor: bpy.props.IntProperty(name="Any Neighbor",description="Any Neighbor frequency max", default=PROP_DEFAULTS["freq_any_neighbor"], min=-1,max=26, update=auto_save)
    freq_any_axes: bpy.props.IntVectorProperty(name="Axes",description="Any Object in Axes frequency max", default=PROP_DEFAULTS["freq_any_axes"], size=3, min=-1, update=auto_save)
    freq_neighbor_face : bpy.props.IntProperty(name="Face",description="Neighbor face frequency max", default=PROP_DEFAULTS["freq_neighbor_face"], min=-1,max=6, update=auto_save)
    freq_neighbor_corner : bpy.props.IntProperty(name="Corner",description="Neighbor corner frequency max", default=PROP_DEFAULTS["freq_neighbor_corner"], min=-1,max=8, update=auto_save)
    freq_neighbor_edge : bpy.props.IntProperty(name="Edge",description="Neighbor edge frequency max", default=PROP_DEFAULTS["freq_neighbor_edge"], min=-1,max=12, update=auto_save)
    freq_any_neighbor_face : bpy.props.IntProperty(name="Face",description="Neighbor face frequency max", default=PROP_DEFAULTS["freq_any_neighbor_face"], min=-1,max=6, update=auto_save)
    freq_any_neighbor_corner : bpy.props.IntProperty(name="Corner",description="Neighbor corner frequency max", default=PROP_DEFAULTS["freq_any_neighbor_corner"], min=-1,max=8, update=auto_save)
    freq_any_neighbor_edge : bpy.props.IntProperty(name="Edge",description="Neighbor edge frequency max", default=PROP_DEFAULTS["freq_any_neighbor_edge"], min=-1,max=12, update=auto_save)
    sym_mirror_axes : bpy.props.BoolVectorProperty(name="Axes",description="Symmetry Axes", default=PROP_DEFAULTS["sym_mirror_axes"], update=auto_save)
    sym_mirror_axes_rotate: bpy.props.BoolProperty(name="Rotate Object", description="Rotate Objects", default=PROP_DEFAULTS["sym_mirror_axes_rotate"], update=auto_save)
    sym_mirror_axes_x:  bpy.props.PointerProperty(name="x", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_y: bpy.props.PointerProperty(name="y", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_z: bpy.props.PointerProperty(name="z", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_xy: bpy.props.PointerProperty(name="xy", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_xz: bpy.props.PointerProperty(name="xz", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_yz: bpy.props.PointerProperty(name="yz", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_xyz: bpy.props.PointerProperty(name="xyz", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_rotate_axis : bpy.props.FloatVectorProperty(name="Axis",description="Rotation Axis", default=PROP_DEFAULTS["sym_rotate_axis"], update=auto_save)
    sym_rotate_n : bpy.props.IntProperty(name="Number",description="Number of rotations", default=PROP_DEFAULTS["sym_rotate_n"], min=-1, update=auto_save)
    region_min: bpy.props.IntVectorProperty(name="min",description="Region minimum", default=PROP_DEFAULTS["region_min"],min=-1, update=auto_save)
    region_max: bpy.props.IntVectorProperty(name="max",description="Region minimum", default=PROP_DEFAULTS["region_max"],min=-1, update=auto_save)
    region_quadrant: bpy.props.BoolVectorProperty(name="Quadrant",description="Quadrant (fbl,fbr,ftl,ftr,bbl,bbr,btl,btr)", size=8, default=PROP_DEFAULTS["region_quadrant"], update=auto_save)
    conn_directions: bpy.props.EnumProperty(name="", description="Select a direction", items=get_conn_directions, update=handle_conn_directions_update)
    conn_name: bpy.props.StringProperty(name="Connector name",description="Connector name", default="", update=auto_save)
    conn_known_names : bpy.props.EnumProperty(items=get_known_conn_names, name='Select to apply', update=take_known_conn_name)
    auto_save: bpy.props.BoolProperty(name="Auto save",description="Auto save constraint properties", default=False)

    vis_directions : bpy.props.BoolProperty(name="",description="Show directions", default = False)

    validator_output_list: bpy.props.CollectionProperty(type=WFC3DValidatorOutputItem)
    validator_output_list_idx: bpy.props.IntProperty()

class WFC3DAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    cherry_picking_delay: bpy.props.IntProperty(name="Cherry Picking Delay", description="Cherry picking delay in seconds", min=0, default=CHERRY_PICKING_DELAY,)
    default_empty_name : bpy.props.StringProperty(name="Default Empty Name", description="Default Empty Name", default=DEFAULT_EMPTY_NAME,)
    def draw(self, _context):
        layout = self.layout
        layout.prop(self, "cherry_picking_delay")
        layout.prop(self, "default_empty_name")

properties = [ WFC3DValidatorOutputItem, WFC3DAddonPreferences, WFC3DEditPanelMultiSelItem, WFC3DEditPanelNeighborMultiSelItem, WFC3DProperties, ]