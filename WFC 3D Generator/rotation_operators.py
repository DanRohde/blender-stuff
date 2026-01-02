import bpy
import math
from .helper import get_selected_items, get_object_by_name
from .constants import ROTATE_DIRECTIONS, ROTATE_DIMENSIONS, PROP_DEFAULTS, FACE_DIRECTIONS, DIRECTIONS


def rotate_properties(props, obj, axis, angle):
    angles = [ 90, 180, 270 ]
    rd = ROTATE_DIRECTIONS[axis]
    rdim = ROTATE_DIMENSIONS[axis]
    directions = list(DIRECTIONS)
    ## read custom properties:
    objprops = {}
    for d in ROTATE_DIRECTIONS[axis]:
        dl = d.lower()
        if props.rt_geometry and d in FACE_DIRECTIONS: objprops[f"geo_{dl}"] = obj.get(f"wfc_geo_{dl}", PROP_DEFAULTS[f"geo_{dl}"])
        if props.rt_connector: objprops[f"conn_{dl}"] = obj.get(f"wfc_conn_{dl}", PROP_DEFAULTS[f"conn_{dl}"])
        if props.rt_neighbor: objprops[dl] = obj.get(f"wfc_{dl}", PROP_DEFAULTS[dl])

    if props.rt_conn_excl:
        objprops["conn_excl"] = []
        idx = 0
        while f"wfc_conn_excl_direction_{idx}" in obj:
            objprops["conn_excl"].append(obj[f"wfc_conn_excl_direction_{idx}"])
            idx += 1

    if props.rt_mult_conn:
        objprops["mult_conn"] = []
        idx = 0
        while f"wfc_mult_conn_direction_{idx}" in obj:
            objprops["mult_conn"].append(obj[f"wfc_mult_conn_direction_{idx}"])
            idx += 1
    if props.rt_empty:
        objprops["empty"] = obj["wfc_empty_neighbor"].split(",")  if "wfc_empty_neighbor" in obj else []
        objprops["empty_any"] = obj["wfc_empty_any_neighbor"].split(",") if "wfc_empty_any_neighbor" in obj else []
    if props.rt_dimensions:
        objprops["dimensions"] = list(obj["wfc_dim_xyz"]) if "wfc_dim_xyz" in obj else None
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
            if props.rt_conn_excl:
                for idx in range(len(objprops["conn_excl"])):
                    obj[f"wfc_conn_excl_direction_{idx}"] = directions.index(rd[directions[objprops["conn_excl"][idx]]])
            if props.rt_mult_conn:
                for idx in range(len(objprops["mult_conn"])):
                    obj[f"wfc_mult_conn_direction_{idx}"] = directions.index(rd[directions[objprops["mult_conn"][idx]]])
            if props.rt_empty:
                if len(objprops["empty"]) > 0: obj["wfc_empty_neighbor"] = ",".join([rd[d] for d in objprops["empty"]])
                if len(objprops["empty_any"]) > 0: obj["wfc_empty_any_neighbor"] = ",".join([rd[d] for d in objprops["empty_any"]])
            if props.rt_dimensions and objprops["dimensions"] is not None:
                obj["wfc_dim_xyz"] = [objprops["dimensions"][rdim[0]], objprops["dimensions"][rdim[1]], objprops["dimensions"][rdim[2]]]
        ## rotate object properties:
        cache = {}
        for d in rd:
            dl = d.lower()
            rdl = rd[d].lower()

            if dl in cache:
                if props.rt_neighbor: objprops[rdl] = cache[dl]
                if props.rt_connector: objprops[f"conn_{rdl}"] = cache[f"conn_{dl}"]
                if props.rt_geometry and d in FACE_DIRECTIONS: objprops[f"geo_{rdl}"] = cache[f"geo_{dl}"]
            else:
                if props.rt_neighbor:
                    cache[rdl] = objprops[rdl]
                    objprops[rdl] = objprops[dl]
                if props.rt_connector:
                    cache[f"conn_{rdl}"] = objprops[f"conn_{rdl}"]
                    objprops[f"conn_{rdl}"] = objprops[f"conn_{dl}"]
                if props.rt_geometry and d in FACE_DIRECTIONS:
                    cache[f"geo_{rdl}"] = objprops[f"geo_{rdl}"]
                    objprops[f"geo_{rdl}"] = objprops[f"geo_{dl}"]
        if props.rt_conn_excl:
            for idx in range(len(objprops["conn_excl"])):
                objprops["conn_excl"][idx] = directions.index(rd[directions[objprops["conn_excl"][idx]]])
        if props.rt_mult_conn:
            for idx in range(len(objprops["mult_conn"])):
                objprops["mult_conn"][idx] = directions.index(rd[directions[objprops["mult_conn"][idx]]])
        if props.rt_empty:
            if len(objprops["empty"]) > 0 : objprops["empty"] = [ rd[d] for d in objprops["empty"]]
            if len(objprops["empty_any"]) > 0: objprops["empty_any"] = [rd[d] for d in objprops["empty_any"]]
        if props.rt_dimensions and objprops["dimensions"] is not None:
            objprops["dimensions"] = [objprops["dimensions"][rdim[0]], objprops["dimensions"][rdim[1]], objprops["dimensions"][rdim[2]]]

def rotate_object(props, obj, offset):
    created_objects = []
    angles = [90,180,270]
    o = obj
    for sel,angle in zip(props.rt_rotation_x, angles):
        if not sel: continue
        new_obj = obj.copy()
        if hasattr(obj, "data") and obj.data is not None: new_obj.data = obj.data.copy()
        new_obj.rotation_euler[0] = -math.radians(angle)
        new_obj.location = ( o.location[0] + offset[0], o.location[1] + offset[1], o.location[2] + offset[2] )
        props.collection_obj.objects.link(new_obj)

        rotate_properties(props, new_obj, 'X', angle)

        created_objects.append(new_obj)
        o = new_obj

    for sel,angle in zip(props.rt_rotation_y, angles):
        if not sel: continue
        new_obj = obj.copy()
        if hasattr(obj, "data") and obj.data is not None: new_obj.data = obj.data.copy()
        new_obj.rotation_euler[1] = -math.radians(angle)
        new_obj.location = ( o.location[0] + offset[0], o.location[1] + offset[1], o.location[2] + offset[2] )
        props.collection_obj.objects.link(new_obj)

        rotate_properties(props, new_obj, 'Y', angle)

        created_objects.append(new_obj)
        o = new_obj

    for sel,angle in zip(props.rt_rotation_z, angles):
        if not sel: continue
        new_obj = obj.copy()
        if hasattr(obj, "data") and obj.data is not None: new_obj.data = obj.data.copy()
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
        try:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        except Exception as e:
            pass
        o.select_set(False)
        bpy.context.view_layer.objects.active = None

    return offset
class OBJECT_OT_Rotation(bpy.types.Operator):
    """Create rotated copies."""
    bl_idname = "object.wfc_rotation"
    bl_label = "Create Rotated Copies"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        selected_objects = get_selected_items(props.rt_list)
        if len(selected_objects) == 0: return {'FINISHED'}
        offset = props.rt_offset
        for so in selected_objects:
            if so in props.collection_obj.children: continue
            obj = props.collection_obj.objects[so]
            offset = rotate_object(props, obj, offset)

        return {'FINISHED'}
class OBJECT_OT_RotationGetSelectedObject(bpy.types.Operator):
    bl_idname = "object.wfc_rotation_get_selected_object"
    bl_label = ""
    bl_description = "Select objects selected in the 3D Viewport"
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

class OBJECT_OT_RotationSelectDropdownObject(bpy.types.Operator):
    bl_idname = "object.wfc_rotation_select_dropdown_object"
    bl_label = ""
    bl_description = "Select objects in the 3D Viewport"
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

operators = [ OBJECT_OT_Rotation, OBJECT_OT_RotationGetSelectedObject, OBJECT_OT_RotationSelectDropdownObject ]