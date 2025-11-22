import bpy

from .constants import *
from .helper import auto_save, update_edit_form, handle_edit_neighbor_constraint_update, handle_conn_directions_update, handle_update_collection, get_noise_basis
from .gen_operators import  handle_seed_change


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
            elif d in DIR_TRANSLATION:
                label = DIR_TRANSLATION[d]
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
    obj: bpy.props.PointerProperty(type=bpy.types.ID)
    selected: bpy.props.BoolProperty(default=False, update=update_edit_form)

class WFC3DEditPanelNeighborMultiSelItem(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.ID)
    selected: bpy.props.BoolProperty(default=False, update=auto_save)

class WFC3DRotationPanelMultiSelItem(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.ID)
    selected: bpy.props.BoolProperty(default=False)

class WFC3DValidatorOutputItem(bpy.types.PropertyGroup):
    severity: bpy.props.IntProperty()
    logentry: bpy.props.StringProperty()
    description: bpy.props.StringProperty()

class WFC3DRegionFrequencyListItem(bpy.types.PropertyGroup):
    regfreq_name: bpy.props.StringProperty(name='Name', description="Optional name of the region", default=PROP_DEFAULTS["regfreq_name"], update=auto_save)
    regfreq_min: bpy.props.IntVectorProperty(size=3, update=auto_save, name="min", description="Region min", min=-1)
    regfreq_max: bpy.props.IntVectorProperty(size=3, update=auto_save, name="max", description="Region max", min=-1)
    regfreq_freq: bpy.props.IntProperty(update=auto_save, name="Frequency", description="Region frequency", min=-1)
    selected: bpy.props.BoolProperty(default=False)

class WFC3DFixedPositionListItem(bpy.types.PropertyGroup):
    fixed_position_xyz: bpy.props.IntVectorProperty(name="",
                                                    description="Fixed Position for a building block", min=-1,
                                                    default=PROP_DEFAULTS['fixed_position_xyz'], update=auto_save)
    selected: bpy.props.BoolProperty(default=False)

class WFC3DRegionProbabilityListItem(bpy.types.PropertyGroup):
    regprob_name: bpy.props.StringProperty(name='Name', description='Optional name of the region', default=PROP_DEFAULTS['regprob_name'], update=auto_save)
    regprob_min: bpy.props.IntVectorProperty(size=3, update=auto_save, name="min", description="Region min", min=-1)
    regprob_max: bpy.props.IntVectorProperty(size=3, update=auto_save, name="max", description="Region max", min=-1)
    regprob_weight: bpy.props.IntProperty(update=auto_save, name="Weight", description="Region weight", min=0)
    regprob_probability: bpy.props.FloatProperty(update=auto_save, name="Probability", description="Region probability", min=0, max=1)
    selected: bpy.props.BoolProperty(default=False)

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
    random_start_cell: bpy.props.BoolProperty(name="Random Start Cell", description="Random start cell", default=False, update=handle_seed_change)
    random_direction: bpy.props.BoolProperty(name="Random Direction", description="Random direction", default=False,)
    seed: bpy.props.IntProperty(name="Random Seed", description="Random seed", default=0, update=handle_seed_change)
    auto_generate: bpy.props.BoolProperty(name="Automatic Model Generation when Random Seed Changes", default=False,)
    cherry_picking_running: bpy.props.BoolProperty(name="Cherry Picking Running", default=False,)
    link_objects: bpy.props.BoolProperty(name="Link New Objects (recommended)", description="Link new objects instead of copying them.", default = True,)
    copy_modifiers: bpy.props.BoolProperty(name="Copy Modifiers", description="Copy modifiers to linked objects.",)
    remove_target_collection: bpy.props.BoolProperty(name="Remove Target Collection", description="Remove existing target collection",)
    search_iterations: bpy.props.IntProperty(name="Search Iterations", description="Search iterations", min=1, default=100, max=1000)
    search_result: bpy.props.IntVectorProperty(name="Search Result", description="Search result", default=(-1,-1,-1), size=3)

    obj_list: bpy.props.CollectionProperty(type=WFC3DEditPanelMultiSelItem)
    obj_list_idx: bpy.props.IntProperty()
    edit_type: bpy.props.EnumProperty(name="", description="Select constraints type",
        items=[('objects','Object Constraints','Object constraints'),('defaults','Collection Defaults','Collection defaults')],
        update=update_edit_form,
    )
    edit_constraints: bpy.props.EnumProperty(
        name="", description = "Select constraint type",
        items=[("_none_","Select a Constraint Type","Select a constraint type"),
               None,
               ("neighbor","Neighbor Constraints","Neighbor constraints"),
               ('connector', 'Connector Constraints', 'Connector constraints'),
               ('geometry', 'Geometry Constraints', 'Geometry constraints'),
               None,
               ('dimensions', 'Dimensions Constraints', 'Dimensions constraints'),
               ('fixed_position', 'Fixed Position Constraints', 'Fixed position constraints'),
               ("grid","Grid Constraints","Grid constraints"),("region","Region Constraints","Region constraints"),
               ('frequency',"Frequency Constraints","Frequency constraints"), ('regfreq','Region Frequency Constraints','Region Frequency constraints'),
               ("symmetry","Symmetry Constraints","Symmetry constraints"),
               None,
               ("probability", "Probability Constraints", "Probability constraints"),
               ("regprob", "Region Probability Constraints", "Region Probability constraints"),
               None,
               ("transformation", "Transformations", "Transformations"),
               ("noise","Noise Constraints","Noise constraints"),
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
    rotation_min : bpy.props.FloatVectorProperty(name="Min", description="Rotation degrees min", default=PROP_DEFAULTS["rotation_min"], subtype="EULER", update=auto_save)
    rotation_max : bpy.props.FloatVectorProperty(name="Max", description="Rotation degrees max", default=PROP_DEFAULTS["rotation_max"], subtype="EULER", update=auto_save)
    rotation_steps : bpy.props.FloatVectorProperty(name="Steps", description="Rotation degrees Steps", default=PROP_DEFAULTS["rotation_steps"], subtype="EULER", update=auto_save)
    scale_type: bpy.props.EnumProperty(name="",description="",items=[('_none_','No Scaling','Please select a scaling type'),('uniform','Uniform Scaling','Uniform scaling'),('non-uniform','Non-Uniform Scaling','Non-uniform scaling')], update=auto_save)
    scale_min : bpy.props.FloatVectorProperty(name="Min", description="Scale minimum", default=PROP_DEFAULTS["scale_min"], update=auto_save)
    scale_max : bpy.props.FloatVectorProperty(name="Max", description="Scale maximum", default=PROP_DEFAULTS["scale_max"], update=auto_save)
    scale_steps : bpy.props.FloatVectorProperty(name="Steps", description="Scale steps", default=PROP_DEFAULTS["scale_steps"], update=auto_save)
    scale_uni : bpy.props.FloatVectorProperty(name="Scale min/max/steps", description="Uniform scaling", default=PROP_DEFAULTS["scale_uni"], update=auto_save)
    translation_min : bpy.props.FloatVectorProperty(name="Min", description="Translation minimum", default=PROP_DEFAULTS["translation_min"], subtype="TRANSLATION", update=auto_save)
    translation_max : bpy.props.FloatVectorProperty(name="Max", description="Translation maximum", default=PROP_DEFAULTS["translation_max"], subtype="TRANSLATION", update=auto_save)
    translation_steps : bpy.props.FloatVectorProperty(name="Steps", description="Translation steps", default=PROP_DEFAULTS["translation_steps"], subtype="TRANSLATION", update=auto_save)
    flipping: bpy.props.FloatVectorProperty(name="Flipping", description="Flipping probability on given axes", default=PROP_DEFAULTS["flipping"], update=auto_save, min=0, max=1)
    freq_grid: bpy.props.IntProperty(name="Grid",description="Grid frequency max", default=PROP_DEFAULTS["freq_grid"], min=-1, update=auto_save)
    freq_neighbor: bpy.props.IntProperty(name="Neighbor",description="Neighbor frequency max", default=PROP_DEFAULTS["freq_neighbor"], min=-1,max=26, update=auto_save)
    freq_axes: bpy.props.IntVectorProperty(name="Axes",description="Axes frequency max", default=PROP_DEFAULTS["freq_axes"], size=3, min=-1, update=auto_save)
    freq_any_neighbor: bpy.props.IntProperty(name="Any Neighbor",description="Any Neighbor frequency max", default=PROP_DEFAULTS["freq_any_neighbor"], min=-1,max=26, update=auto_save)
    freq_any_axes: bpy.props.IntVectorProperty(name="Any Axes",description="Any Object in Axes frequency max", default=PROP_DEFAULTS["freq_any_axes"], size=3, min=-1, update=auto_save)
    freq_neighbor_face : bpy.props.IntProperty(name="Face",description="Neighbor face frequency max", default=PROP_DEFAULTS["freq_neighbor_face"], min=-1,max=6, update=auto_save)
    freq_neighbor_corner : bpy.props.IntProperty(name="Corner",description="Neighbor corner frequency max", default=PROP_DEFAULTS["freq_neighbor_corner"], min=-1,max=8, update=auto_save)
    freq_neighbor_edge : bpy.props.IntProperty(name="Edge",description="Neighbor edge frequency max", default=PROP_DEFAULTS["freq_neighbor_edge"], min=-1,max=12, update=auto_save)
    freq_any_neighbor_face : bpy.props.IntProperty(name="Any Face",description="Neighbor face frequency max", default=PROP_DEFAULTS["freq_any_neighbor_face"], min=-1,max=6, update=auto_save)
    freq_any_neighbor_corner : bpy.props.IntProperty(name="Any Corner",description="Neighbor corner frequency max", default=PROP_DEFAULTS["freq_any_neighbor_corner"], min=-1,max=8, update=auto_save)
    freq_any_neighbor_edge : bpy.props.IntProperty(name="Any Edge",description="Neighbor edge frequency max", default=PROP_DEFAULTS["freq_any_neighbor_edge"], min=-1,max=12, update=auto_save)
    sym_mirror_axes : bpy.props.BoolVectorProperty(name="Axes",description="Symmetry Axes", default=PROP_DEFAULTS["sym_mirror_axes"], update=auto_save)
    sym_mirror_axes_rotate: bpy.props.BoolProperty(name="Rotate Object", description="Rotate Objects", default=PROP_DEFAULTS["sym_mirror_axes_rotate"], update=auto_save)
    sym_mirror_axes_x:  bpy.props.PointerProperty(name="x", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_y: bpy.props.PointerProperty(name="y", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_z: bpy.props.PointerProperty(name="z", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_xy: bpy.props.PointerProperty(name="xy", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_xz: bpy.props.PointerProperty(name="xz", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_yz: bpy.props.PointerProperty(name="yz", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_axes_xyz: bpy.props.PointerProperty(name="xyz", description="Select a mirror partner", type=bpy.types.Object, update=auto_save)
    sym_mirror_flip_x:  bpy.props.BoolProperty(name="x", description="Flip object on X axis", update=auto_save)
    sym_mirror_flip_y: bpy.props.BoolProperty(name="y", description="Flip object on Y axis", update=auto_save)
    sym_mirror_flip_z: bpy.props.BoolProperty(name="z", description="Flip object on Z axis", update=auto_save)
    sym_mirror_flip_xy: bpy.props.BoolProperty(name="xy", description="Flip object on X & Y axes", update=auto_save)
    sym_mirror_flip_xz: bpy.props.BoolProperty(name="xz", description="Flip object on X & Z axes", update=auto_save)
    sym_mirror_flip_yz: bpy.props.BoolProperty(name="yz", description="Flip object on Y & Z axes", update=auto_save)
    sym_mirror_flip_xyz: bpy.props.BoolProperty(name="xyz", description="Flip object on X & Y & Z axes", update=auto_save)
    sym_mirror_trans: bpy.props.BoolProperty(name="Transfer Random Transformations", description="Transfer random scaling, rotation and translation to mirror partners", update=auto_save)
    sym_mirror_flip_transl: bpy.props.BoolProperty(name="Apply Flipping to Translation", description="Apply the flipping to the translation transformation", update=auto_save)
    sym_rotate_axis : bpy.props.FloatVectorProperty(name="Axis",description="Rotation Axis", default=PROP_DEFAULTS["sym_rotate_axis"], update=auto_save)
    sym_rotate_n : bpy.props.IntProperty(name="Number",description="Number of rotations", default=PROP_DEFAULTS["sym_rotate_n"], min=-1, update=auto_save)
    region_min: bpy.props.IntVectorProperty(name="min",description="Region minimum", default=PROP_DEFAULTS["region_min"],min=-1, update=auto_save)
    region_max: bpy.props.IntVectorProperty(name="max",description="Region minimum", default=PROP_DEFAULTS["region_max"],min=-1, update=auto_save)
    region_quadrant: bpy.props.BoolVectorProperty(name="Quadrant",description="Quadrant (fbl,fbr,ftl,ftr,bbl,bbr,btl,btr)", size=8, default=PROP_DEFAULTS["region_quadrant"], update=auto_save)
    conn_directions: bpy.props.EnumProperty(name="", description="Select a direction", items=get_conn_directions, update=handle_conn_directions_update)
    conn_name: bpy.props.StringProperty(name="Connector name",description="Connector name", default="", update=auto_save)
    conn_known_names : bpy.props.EnumProperty(items=get_known_conn_names, name='Select to apply', update=take_known_conn_name)

    auto_save: bpy.props.BoolProperty(name="Auto save",description="Auto save constraint properties")
    info_toggle: bpy.props.BoolProperty(name="Info", description="Shows constraint properties")
    regfreq_input_list: bpy.props.CollectionProperty(type=WFC3DRegionFrequencyListItem)
    regfreq_input_list_idx: bpy.props.IntProperty()

    vis_directions : bpy.props.BoolProperty(name="",description="Show directions", default = False)

    validator_output_list: bpy.props.CollectionProperty(type=WFC3DValidatorOutputItem)
    validator_output_list_idx: bpy.props.IntProperty()

    prefs_migrated : bpy.props.BoolProperty(name="Preferences migrated", default = False)

    dim_xyz : bpy.props.IntVectorProperty(name="Dimensions",description="Dimensions of a building block.",min=1,default=PROP_DEFAULTS["dim_xyz"], update=auto_save)

    fixed_position_input_list: bpy.props.CollectionProperty(type=WFC3DFixedPositionListItem)
    fixed_position_input_list_idx: bpy.props.IntProperty()

    noise_prob_basis: bpy.props.EnumProperty(name="Noise Basis", description="Select a noise basis", items=get_noise_basis, update=auto_save, )
    noise_prob_threshold: bpy.props.FloatProperty(name="Threshold", description="Threshold", min=0.0, max=1.0, default=PROP_DEFAULTS['noise_prob_threshold'], update=auto_save)
    noise_prob_scale: bpy.props.FloatProperty(name="Scale", description="Scale", min=0, default=PROP_DEFAULTS['noise_prob_scale'], update=auto_save)

    noise_transf_basis: bpy.props.EnumProperty(name="Noise Basis", description="Select a noise basis", items=get_noise_basis, update=auto_save, )
    noise_transf_scale: bpy.props.FloatProperty(name="Scale", description="Scale", min=0, default=PROP_DEFAULTS['noise_transf_scale'], update=auto_save)

    geo_front: bpy.props.BoolProperty(name="front", description="Front face", default=PROP_DEFAULTS["geo_front"], update=auto_save)
    geo_back: bpy.props.BoolProperty(name="back", description="Back face", default=PROP_DEFAULTS["geo_back"], update=auto_save)
    geo_left: bpy.props.BoolProperty(name="left", description="Left face", default=PROP_DEFAULTS["geo_left"], update=auto_save)
    geo_right: bpy.props.BoolProperty(name="right", description="Right face", default=PROP_DEFAULTS["geo_right"], update=auto_save)
    geo_top: bpy.props.BoolProperty(name="top", description="Top face", default=PROP_DEFAULTS["geo_top"], update=auto_save)
    geo_bottom: bpy.props.BoolProperty(name="bottom", description="Bottom face", default=PROP_DEFAULTS["geo_bottom"], update=auto_save)
    geo_match_edges: bpy.props.BoolProperty(name="Match Edges", description="Match edges", default=PROP_DEFAULTS["geo_match_edges"], update=auto_save)
    geo_match_faces: bpy.props.BoolProperty(name="Match Faces", description="Match faces", default=PROP_DEFAULTS["geo_match_faces"], update=auto_save)
    geo_tolerance: bpy.props.FloatProperty(name="Tolerance", description="Tolerance", default=PROP_DEFAULTS["geo_tolerance"], update=auto_save)

    regprob_input_list: bpy.props.CollectionProperty(type=WFC3DRegionProbabilityListItem)
    regprob_input_list_idx: bpy.props.IntProperty()

    backup_import_overwrite: bpy.props.BoolProperty(name="Overwrite", description="Overwrite existing properties", default=True)
    backup_import_replace: bpy.props.BoolProperty(name="Replace", description="Replace existing properties", default=False)

    rt_list: bpy.props.CollectionProperty(type=WFC3DRotationPanelMultiSelItem)
    rt_list_idx: bpy.props.IntProperty()
    rt_auto_active_object: bpy.props.BoolProperty(name="", description="Automatically select objects selected in 3D Viewport.", default=False,)
    rt_rotation_x: bpy.props.BoolVectorProperty(size=3, name="X Rotation", description="90°, 180°, 270°")
    rt_rotation_y: bpy.props.BoolVectorProperty(size=3, name="Y Rotation", description="90°, 180°, 270°", default=(True, True, True))
    rt_rotation_z: bpy.props.BoolVectorProperty(size=3, name="Z Rotation", description="90°, 180°, 270°")
    rt_offset: bpy.props.FloatVectorProperty(size=3, name="Offset", description="Offset location for the created building blocks", subtype="TRANSLATION", default=(0,0,2))
    rt_neighbor : bpy.props.BoolProperty(name="Neighbor", description="Rotate neighbor constraints", default=True)
    rt_connector: bpy.props.BoolProperty(name="Connector", description="Rotate connector constraints", default=True)
    rt_geometry: bpy.props.BoolProperty(name="Geometry", description="Rotate geometry constraints", default=True)

def handle_update_pref(self, _context=None):
    props = bpy.context.scene.wfc_props

    props.auto_save = self.auto_save
    props.copy_modifiers = self.copy_modifiers
    props.remove_target_collection = self.remove_target_collection
    props.link_objects = self.link_objects
    props.render_delay = self.render_delay

from bpy.app.handlers import persistent
@persistent
def handle_blend_load(fn):
    props = bpy.context.scene.wfc_props
    if fn== "" or not props.prefs_migrated:
        handle_update_pref(bpy.context.preferences.addons[__package__].preferences)
        props.prefs_migrated = True

class WFC3DAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    link_objects : bpy.props.BoolProperty(name="Link Objects",description="Link objects", default=True, update=handle_update_pref)
    copy_modifiers: bpy.props.BoolProperty(name="Copy Modifiers",description="Copy modifiers", default=False, update=handle_update_pref)
    remove_target_collection: bpy.props.BoolProperty(name="Remove Target Collection", description="Remove target collection", default=True, update=handle_update_pref)
    cherry_picking_delay: bpy.props.IntProperty(name="Cherry Picking Delay", description="Cherry picking delay in seconds", min=0, default=CHERRY_PICKING_DELAY, update=handle_update_pref)
    auto_save:   bpy.props.BoolProperty(name="Auto save",description="Auto save constraint properties", default=True, update=handle_update_pref)
    default_empty_name : bpy.props.StringProperty(name="Default Empty Name", description="Default Empty Name", default=DEFAULT_EMPTY_NAME, update=handle_update_pref)
    render_delay : bpy.props.FloatProperty(name="Render Delay", description="Render Delay in seconds", default=0.0, min=0.0, update=handle_update_pref)
    def draw(self, _context):
        layout = self.layout
        layout.label(text="WFC 3D Gen")
        f = layout.box().column_flow(columns=2)
        f.prop(self, "render_delay")
        f.prop(self, "link_objects")
        f.prop(self, "copy_modifiers")
        f.prop(self, "remove_target_collection")
        f.prop(self, "cherry_picking_delay")

        layout.label(text="WFC 3D Edit")
        f = layout.box().column_flow(columns=2)
        f.prop(self, "auto_save")
        f.prop(self, "default_empty_name")

properties = [ WFC3DRotationPanelMultiSelItem, WFC3DRegionProbabilityListItem, WFC3DFixedPositionListItem, WFC3DRegionFrequencyListItem, WFC3DValidatorOutputItem, WFC3DAddonPreferences, WFC3DEditPanelMultiSelItem, WFC3DEditPanelNeighborMultiSelItem, WFC3DProperties, ]