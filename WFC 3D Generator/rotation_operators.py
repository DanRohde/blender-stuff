import bpy
from .helper import get_selected_items, get_object_by_name, set_select_all_list_items

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

operators = [ WFC3D_OT_RotationCollectionListSelectAll, WFC3D_OT_RotationCollectionListSelectNone, WFC3D_OT_RotationGetSelectedObject, WFC3D_OT_RotationSelectDropdownObject ]