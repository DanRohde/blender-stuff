import bpy

from .constants import DIRECTIONS

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

def check_collection(collection):
    warn_count, error_count = 0, 0
    for obj in collection.objects:
        if obj.scale.x != 1 or obj.scale.y != 1 or obj.scale.z != 1:
            add_log_entry(2, f"Please apply the scaling to {obj.name}.",f"Go to 3D Viewport, select {obj.name}, and press [CTRL + A] + S")
            error_count += 1
        euler = obj.rotation_euler
        if abs(euler.x)>0 or abs(euler.y)>0 or abs(euler.z)>0:
            add_log_entry(2, f"Please apply the rotation to {obj.name}.", f"Go to 3D Viewport, select {obj.name}, and press [CTRL + A] + R")
            error_count += 1

        for d in DIRECTIONS:
            prop_name = "wfc_" + d.lower()
            if prop_name not in obj: continue
            neighbors = obj[prop_name].split(",")
            for n in neighbors:
                if n in collection.objects or n  in collection.children: continue
                add_log_entry(1,f"Neighbor {n} in {d.lower()} neighbor constraint of {obj.name} does not exists in {collection.name}!")
                warn_count += 1
    return warn_count, error_count

def validate_source_collection():
    props = bpy.context.scene.wfc_props
    clear_log()
    add_log_entry(0, f"Validation of  {props.collection_obj.name} started.")
    warn_count, error_count = check_collection(props.collection_obj)
    for child in props.collection_obj.children:
        w, e = check_collection(child)
        warn_count += w
        error_count += e

    add_log_entry(0, f"Validation of  {props.collection_obj.name} finished.")
    add_log_entry(0 if warn_count == 0 and error_count == 0 else 2, f"Found {warn_count} warning(s), {error_count} error(s).")

class WFC3DValidator(bpy.types.Operator):
    bl_idname = "object.wfc3d_validator"
    bl_label = "Validate Source Collection"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        validate_source_collection()
        return {'FINISHED'}

operators = [ WFC3DValidator ]