import bpy


def add_log_entry(severity, entry, description = ""):
    props = bpy.context.scene.wfc_props
    log = props.validator_output_list
    item = log.add()
    item.severity = severity
    item.logentry = entry
    if description != "":
        item = log.add()
        item.severity = 0
        item.logentry = description

def clear_log():
    props = bpy.context.scene.wfc_props
    log = props.validator_output_list
    log.clear()

def validate_source_collection():
    props = bpy.context.scene.wfc_props
    clear_log()
    add_log_entry(0, f"Validation of  {props.collection_obj.name} started.")
    for obj in props.collection_obj.objects:
        if obj.scale.x != 1 or obj.scale.y != 1 or obj.scale.z != 1:
            add_log_entry(2, f"Please apply scale to {obj.name}",f"Go to 3D Viewport, select {obj.name} and press [CTRL + A] + 'S'")
        euler = obj.rotation_euler
        if abs(euler.x)>0 or abs(euler.y)>0 or abs(euler.z)>0:
            add_log_entry(2, f"Please apply rotation to {obj.name}", f"Go to 3D Viewport, select {obj.name} and press [CTRL + A] + 'R'")
    add_log_entry(0, f"Validation of  {props.collection_obj.name} finished.")

class WFC3DValidator(bpy.types.Operator):
    bl_idname = "object.wfc3d_validator"
    bl_label = "Validate Source Collection"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        validate_source_collection()
        return {'FINISHED'}

operators = [ WFC3DValidator ]