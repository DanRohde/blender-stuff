import bpy
from datetime import datetime

from .constants import DIRECTIONS, OPPOSITE_DIRECTIONS, GRID_CONSTRAINTS, FACE_DIRECTIONS, EDGE_DIRECTIONS, CORNER_DIRECTIONS

def add_log_entry(severity, entry, description = ""):
    props = bpy.context.scene.wfc_props
    log = props.validator_output_list
    item = log.add()
    item.severity = severity
    item.logentry = entry
    item.description = description if description != "" else entry

def clear_log():
    props = bpy.context.scene.wfc_props
    log = props.validator_output_list
    log.clear()

def _set_connector_names(obj, direction, connector_name, conn_names, conn_obj_names):
    if direction.startswith("ANY"):
        if direction == "ANY": directions = { **FACE_DIRECTIONS, **EDGE_DIRECTIONS , **CORNER_DIRECTIONS }
        elif direction == "ANY_FACE": directions = FACE_DIRECTIONS
        elif direction == "ANY_EDGE": directions = EDGE_DIRECTIONS
        elif direction == "ANY_CORNER": directions = CORNER_DIRECTIONS
        else: directions = []
        for d in directions:
            _set_connector_names(obj, d, connector_name, conn_names, conn_obj_names)
        return
    if direction in conn_names:
        if connector_name not in conn_names[direction]: conn_names[direction].append(connector_name)
        if connector_name in conn_obj_names[direction]:
            conn_obj_names[direction][connector_name].append(obj.name)
        else:
            conn_obj_names[direction][connector_name] = [obj.name]
    else:
        conn_names[direction] = [connector_name]
        conn_obj_names[direction] = {connector_name: [obj.name]}


def collect_connector_names(obj, direction, conn_names, conn_obj_names):
    if 'wfc_conn_' + direction.lower() in obj:
        cp = 'wfc_conn_' + direction.lower()
        connector_name = obj[cp]
        _set_connector_names(obj, direction, connector_name, conn_names, conn_obj_names)

def collect_multiple_connector_names(obj, conn_names, conn_obj_names):
    directions = list(DIRECTIONS)
    idx = 0
    while f"wfc_mult_conn_direction_{idx}" in obj:
        direction = directions[obj[f"wfc_mult_conn_direction_{idx}"]]
        connector_name = obj[f"wfc_mult_conn_name_{idx}"]
        _set_connector_names(obj, direction, connector_name, conn_names, conn_obj_names)
        idx += 1
def check_adjacency_constraints(collection, obj, conn_names, conn_obj_names):
    warn_count  = 0
    for d in DIRECTIONS:
        collect_connector_names(obj, d, conn_names, conn_obj_names)
        prop_name = "wfc_" + d.lower()
        if prop_name not in obj: continue
        neighbors = obj[prop_name].split(",")
        for n in neighbors:
            if n in collection.objects or n in collection.children: continue
            add_log_entry(1,f"Neighbor {n} in {d.lower()} neighbor constraint of {obj.name} does not exists in {collection.name}!")
            warn_count += 1
    return warn_count

def check_connector_names(conn_names, conn_obj_names):
    warn_count = 0
    for d in conn_names:
        for cn in conn_names[d]:
            if OPPOSITE_DIRECTIONS[d] in conn_names and cn in conn_names[OPPOSITE_DIRECTIONS[d]]: continue
            add_log_entry(1, f"Connector name '{cn}' found in {d.lower()} connector constraint of '{', '.join(conn_obj_names[d][cn])}' has no counterpart in the opposite direction {OPPOSITE_DIRECTIONS[d].lower()}!")
            warn_count += 1
    return warn_count

def check_geometry(obj):
    error_count =  0
    if obj.scale.x != 1 or obj.scale.y != 1 or obj.scale.z != 1:
        add_log_entry(2, f"Please apply the scaling to {obj.name}.",f"Go to 3D Viewport, select {obj.name}, and press [CTRL + A] + S")
        error_count += 1
    euler = obj.rotation_euler
    if abs(euler.x)>0 or abs(euler.y)>0 or abs(euler.z)>0:
        add_log_entry(2, f"Please apply the rotation to {obj.name}.", f"Go to 3D Viewport, select {obj.name}, and press [CTRL + A] + R")
        error_count += 1
    return error_count

def check_grid_constraints(obj):
    warn_count = 0
    mc = 0
    for g in GRID_CONSTRAINTS:
        prop_name = "wfc_" + g.lower()
        if prop_name not in obj: continue
        if obj[prop_name] == '-': mc+=1
    if mc == len(GRID_CONSTRAINTS):
        add_log_entry(1, f"The object {obj.name} cannot be placed in the grid because the grid constraints prohibit all locations.")
        warn_count += 1
    return warn_count

def check_region_constraints(obj):
    warn_count = 0
    if 'wfc_region_quadrant' not in obj: return 0
    if sum(obj['wfc_region_quadrant'])==0:
        add_log_entry(1, f"The object {obj.name} cannot be placed in the grid because the region constraints prohibit all quadrants.")
        warn_count += 1
    return warn_count

def check_probability_constraints(obj):
    warn_count = 0

    if 'wfc_weight' in obj and obj['wfc_weight'] == 0:
        add_log_entry(1, f"The object {obj.name} cannot be placed in the grid because the 0 weight constraint prohibit all locations.")
        warn_count += 1

    if 'wfc_probability' in obj and obj['wfc_probability'] == 0:
        add_log_entry(1,f"The object {obj.name} cannot be placed in the grid because the 0 probability constraint prohibit all locations.")
        warn_count += 1

    return warn_count

def check_frequency_constraints(_obj):
    warn_count = 0

    return warn_count
def check_dimensions_constraints(obj):
    if 'wfc_dim_xyz' not in obj: return 0
    if sum(obj['wfc_dim_xyz'])==3: return 0
    warn_count = 0
    props = bpy.context.scene.wfc_props
    x, y, z = obj['wfc_dim_xyz']
    if x > props.grid_size[0]  or y > props.grid_size[1] or z > props.grid_size[2]:
        add_log_entry(1, f"The dimensions of object {obj.name} exceed the current grid size {props.grid_size[0]}x{props.grid_size[1]}x{props.grid_size[2]}.")
        warn_count +=1

    return warn_count
def check_fixed_position_constraints(obj):
    warn_count = 0
    return warn_count
def check_region_frequency_constraints(obj):
    warn_count = 0
    gs = bpy.context.scene.wfc_props.grid_size
    idx = 0
    while f'wfc_regfreq_freq_{idx}' in obj:
        minx, miny, minz = obj[f"wfc_regfreq_min_{idx}"]
        maxx, maxy, maxz = obj[f"wfc_regfreq_max_{idx}"]
        name = obj[f"wfc_regfreq_name_{idx}"] if f"wfc_regfreq_name_{idx}" in obj else ""
        rsize = (maxx-minx+1) * (maxy-miny+1) * (maxz-minz+1)
        freq = obj[f"wfc_regfreq_freq_{idx}"]
        if freq < 0 or freq > rsize:
            add_log_entry(1,f"The frequency {freq} of the region frequency constraint {idx} (name: {name}) of object {obj.name} is out of range 0..{rsize}.")
            warn_count += 1
        idx += 1

    return warn_count
def check_region_probability_constraints(obj):
    warn_count = 0

    return warn_count
def check_distance_constraints(obj):
    warn_count = 0
    gs = bpy.context.scene.wfc_props.grid_size
    sc = bpy.context.scene.wfc_props.collection_obj
    idx = 0
    while f'wfc_distance_{idx}' in obj:
        x, y, z = obj[f"wfc_distance_{idx}"]
        if x < 0 or x > gs[0] or y < 0 or y > gs[1] or z < 0 or z > gs[2]:
            add_log_entry(1, f"Distance constraints of {obj.name}: Distance of entry {idx} is larger than the grid size.")
            warn_count += 1
        f = obj[f"wfc_distance_from_{idx}"]
        if f == 0:
            o = obj[f"wfc_distance_object_{idx}"]
            if o is None or o.name not in sc.objects:
                add_log_entry(1, f"Distance constraints of {obj.name}: Object {o.name if o is not None else o} of entry {idx} is not in the source collection.")
                warn_count += 1
        else:
            o = obj[f"wfc_distance_subcollection_{idx}"]
            if o is None or o.name not in sc.children:
                add_log_entry(1, f"Distance constraints of {obj.name}: Sub-collection of entry {idx} is not in the source collection.")
                warn_count += 1
        idx += 1
    return warn_count
def check_noise_constraints(obj):
    warn_count = 0
    if "wfc_noise_prob_scale" in obj:
        if int(obj["wfc_noise_prob_scale"]) == obj["wfc_noise_prob_scale"]:
            add_log_entry(1, f"An integer scale value such as {int(obj['wfc_noise_transf_scale'])} from {obj.name} prevents the effect of noise.")
            warn_count += 1
    if "wfc_noise_transf_scale" in obj:
        if int(obj["wfc_noise_transf_scale"]) == obj["wfc_noise_transf_scale"]:
            add_log_entry(1, f"An integer scale value such as {int(obj['wfc_noise_transf_scale'])} from {obj.name} prevents the effect of noise.")
            warn_count += 1
    return warn_count
def check_collection(collection):
    warn_count, error_count = 0, 0
    conn_names = {}
    conn_obj_names = {}
    for obj in collection.objects:
        error_count += check_geometry(obj)
        warn_count += check_adjacency_constraints(collection, obj, conn_names, conn_obj_names)
        warn_count += check_grid_constraints(obj)
        warn_count += check_region_constraints(obj)
        warn_count += check_probability_constraints(obj)
        warn_count += check_region_probability_constraints(obj)
        warn_count += check_frequency_constraints(obj)
        warn_count += check_dimensions_constraints(obj)
        warn_count += check_fixed_position_constraints(obj)
        warn_count += check_region_frequency_constraints(obj)
        warn_count += check_noise_constraints(obj)
        warn_count += check_distance_constraints(obj)
        collect_multiple_connector_names(obj, conn_names, conn_obj_names)
    warn_count += check_connector_names(conn_names, conn_obj_names)
    return warn_count, error_count

def validate_source_collection():
    props = bpy.context.scene.wfc_props
    clear_log()
    add_log_entry(0, f"Validation of {props.collection_obj.name} started.", datetime.now().strftime("%c"))
    warn_count, error_count = check_collection(props.collection_obj)
    for child in props.collection_obj.children:
        w, e = check_collection(child)
        warn_count += w
        error_count += e

    add_log_entry(0, f"Validation of {props.collection_obj.name} finished.", datetime.now().strftime("%c"))
    sev = 0
    if warn_count > 0: sev = 1
    if error_count > 0: sev = 2
    add_log_entry(sev, f"Found {warn_count} warning(s), {error_count} error(s).", datetime.now().strftime("%c"))

class WFC3D_OT_Validator(bpy.types.Operator):
    """Validate all objects in the source collection."""
    bl_idname = "object.wfc3d_validator"
    bl_label = "Validate Source Collection"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, _context):
        validate_source_collection()
        return {'FINISHED'}

class WFC3D_OT_ValidatorClearLog(bpy.types.Operator):
    """Clear WFC3D validator log."""
    bl_idname = "object.wfc3d_validator_clear_log"
    bl_label = "Clear Log"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        props.validator_output_list.clear()
        return {'FINISHED'}


operators = [ WFC3D_OT_ValidatorClearLog, WFC3D_OT_Validator ]