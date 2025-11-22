import bpy
import math
from .helper import get_selected_items, get_object_by_name, set_select_all_list_items
from .constants import ROTATE_DIRECTIONS, PROP_DEFAULTS, FACE_DIRECTIONS


def rotate_properties(props, obj, axis, angle):
    angles = [ 90, 180, 270 ]
    rd = ROTATE_DIRECTIONS[axis]

    ## read custom properties:
    objprops = {}
    for d in ROTATE_DIRECTIONS[axis]:
        dl = d.lower()
        if d in FACE_DIRECTIONS: objprops[f"geo_{dl}"] = obj.get(f"wfc_geo_{dl}", PROP_DEFAULTS[f"geo_{dl}"])
        objprops[f"conn_{dl}"] = obj.get(f"wfc_conn_{dl}", PROP_DEFAULTS[f"conn_{dl}"])
        objprops[dl] = obj.get(f"wfc_{dl}", PROP_DEFAULTS[dl])

    ## rotate:
    for a in angles:
        if a == angle:
            # rotate custom properties:
            for d in rd:
                dl = d.lower()
                rdl = rd[d].lower()
                if props.rt_neighbor:
                    rpn = f"wfc_{rdl}"
                    obj[rpn] = objprops[dl]
                    if objprops[dl] == PROP_DEFAULTS[dl]: del obj[rpn]

                if props.rt_connector:
                    rpn = f"wfc_conn_{rdl}"
                    obj[rpn] = objprops[f"conn_{dl}"]
                    if objprops[f"conn_{dl}"] == PROP_DEFAULTS[f"conn_{dl}"]: del obj[rpn]

                if props.rt_geometry and d in FACE_DIRECTIONS:
                    rpn = f"wfc_geo_{rdl}"
                    obj[rpn] = objprops[f"geo_{dl}"]
                    if objprops[f"geo_{dl}"] == PROP_DEFAULTS[f"geo_{dl}"]: del obj[rpn]
        ## rotate object properties:
        cache = {}
        for d in rd:
            dl = d.lower()
            rdl = rd[d].lower()

            if dl in cache:
                objprops[rdl] = cache[dl]
                objprops[f"conn_{rdl}"] = cache[f"conn_{dl}"]
                if d in FACE_DIRECTIONS: objprops[f"geo_{rdl}"] = cache[f"geo_{dl}"]
            else:
                cache[rdl] = objprops[rdl]
                objprops[rdl] = objprops[dl]

                cache[f"conn_{rdl}"] = objprops[f"conn_{rdl}"]
                objprops[f"conn_{rdl}"] = objprops[f"conn_{dl}"]

                if d in FACE_DIRECTIONS:
                    cache[f"geo_{rdl}"] = objprops[f"geo_{rdl}"]
                    objprops[f"geo_{rdl}"] = objprops[f"geo_{dl}"]



def rotate_object(props, obj, offset):
    created_objects = []
    angles = [90,180,270]
    o = obj
    for sel,angle in zip(props.rt_rotation_x, angles):
        if not sel: continue
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.rotation_euler[0] = -math.radians(angle)
        new_obj.location = ( o.location[0] + offset[0], o.location[1] + offset[1], o.location[2] + offset[2] )
        props.collection_obj.objects.link(new_obj)

        rotate_properties(props, new_obj, 'X', angle)

        created_objects.append(new_obj)
        o = new_obj

    for sel,angle in zip(props.rt_rotation_y, angles):
        if not sel: continue
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.rotation_euler[1] = -math.radians(angle)
        new_obj.location = ( o.location[0] + offset[0], o.location[1] + offset[1], o.location[2] + offset[2] )
        props.collection_obj.objects.link(new_obj)

        rotate_properties(props, new_obj, 'Y', angle)

        created_objects.append(new_obj)
        o = new_obj

    for sel,angle in zip(props.rt_rotation_z, angles):
        if not sel: continue
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.rotation_euler[2] = -math.radians(angle)
        new_obj.location = ( o.location[0] + offset[0], o.location[1] + offset[1], o.location[2] + offset[2] )
        props.collection_obj.objects.link(new_obj)

        rotate_properties(props, new_obj, 'Z', angle)

        created_objects.append(new_obj)
        o = new_obj


    bpy.ops.object.select_all(action='DESELECT')
    for o in created_objects:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        o.select_set(False)

    return offset
class WFC3D_OT_Rotation(bpy.types.Operator):
    """Create rotated copies."""
    bl_idname = "rotation.wfc_rotation"
    bl_label = "Create Rotated Copies"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        selected_objects = get_selected_items(props.rt_list)
        if len(selected_objects) == 0: return {'FINISHED'}
        offset = props.rt_offset
        for so in selected_objects:
            if so in props.collection_obj.children: continue
            obj = get_object_by_name(props, so)
            offset = rotate_object(props, obj, offset)

        return {'FINISHED'}
class WFC3D_OT_RotationGetSelectedObject(bpy.types.Operator):
    """Select objects selected in 3D Viewport"""
    bl_idname = "rotation.wfc_get_selected_object"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        selected_objects = bpy.context.selected_objects

        if selected_objects:
            selected_object_names = [obj.name for obj in selected_objects]
            for obj in selected_objects:
                for child in props.collection_obj.children:
                    if obj.name in child.objects:
                        selected_object_names.append(child.name)
            for item in props.rt_list:
                item.selected = item.obj.name in selected_object_names
            props.rt_list_idx = -1
        else:
            self.report({'WARNING'}, "No active object found")
            return {'CANCELLED'}
        return {'FINISHED'}

class WFC3D_OT_RotationSelectDropdownObject(bpy.types.Operator):
    """Select objects in 3D Viewport"""
    bl_idname = "rotation.wfc_select_dropdown_object"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        sel_items = get_selected_items(props.rt_list)
        if len(sel_items) > 0:
            obj = get_object_by_name(props, sel_items[0])
        else:
            self.report({'WARNING'}, "Please select an object in the object list.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for item in get_selected_items(props.rt_list):
            get_object_by_name(props, item).select_set(True)

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
        return {'FINISHED'}
class WFC3D_OT_RotationCollectionListSelectAll(bpy.types.Operator):
    """Select all objects in list"""
    bl_idname = "rotation.wfc_collection_list_select_all"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.rt_list, True)
        return {'FINISHED'}


class WFC3D_OT_RotationCollectionListSelectNone(bpy.types.Operator):
    """Deselect all objects in list"""
    bl_idname = "rotation.wfc_collection_list_select_none"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.rt_list, False)
        return {'FINISHED'}

operators = [ WFC3D_OT_Rotation, WFC3D_OT_RotationCollectionListSelectAll, WFC3D_OT_RotationCollectionListSelectNone, WFC3D_OT_RotationGetSelectedObject, WFC3D_OT_RotationSelectDropdownObject ]