import bpy
from datetime import datetime

from .constants import DIRECTIONS, OPPOSITE_DIRECTIONS, GRID_CONSTRAINTS

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

def collect_connector_names(obj, d, conn_names, conn_obj_names):
    if 'wfc_conn_' + d.lower() in obj:
        cp = 'wfc_conn_' + d.lower()
        if d in conn_names:
            if obj[cp] not in conn_names[d]: conn_names[d].append(obj[cp])
            if obj[cp] in conn_obj_names[d]:
                conn_obj_names[d][obj[cp]].append(obj.name)
            else:
                conn_obj_names[d][obj[cp]] = [obj.name]
        else:
            conn_names[d] = [obj[cp]]
            conn_obj_names[d] = {obj[cp]: [obj.name]}

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
            add_log_entry(1, f"Connector name {cn} found in {d.lower()} connector constraint of '{', '.join(conn_obj_names[d][cn])}' has no counterpart in the opposite direction {OPPOSITE_DIRECTIONS[d].lower()}!")
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
    if 'wfc_dim_xzy' in obj and sum(obj['wfc_dim_xzy'])==3: return 0
    warn_count = 0
    props = bpy.context.scene.wfc_props
    x, y, z = obj['wfc_dim_xzy']

    if props.grid_size[0] <= x or props.grid_size[1] <= y or props.grid_size[2] <= z:
        add_log_entry(1, f"The dimensions of object {obj.name} exceed the current grid size.")
        warn_count +=1

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
        warn_count += check_frequency_constraints(obj)
        warn_count += check_dimensions_constraints(obj)

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

class WFC3DValidator(bpy.types.Operator):
    bl_idname = "object.wfc3d_validator"
    bl_label = "Validate Source Collection"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, _context):
        validate_source_collection()
        return {'FINISHED'}

operators = [ WFC3DValidator ]