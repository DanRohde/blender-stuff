import bpy

from .constants import *
from .properties import handle_update_collection
from .helper import *

from .vis import add_directions_geometry_nodegroup, remove_directions_geometry_nodegroup

def _get_obj_list(props):
    return ",".join(get_selected_items(props.obj_list))


def _reset_constraints(props, constraints):
    items = []
    if props.edit_type == 'objects':
        items = get_selected_items(props.obj_list)
    elif props.edit_type == 'defaults':
        items = [get_default_empty_name()]

    auto_save = props.auto_save
    props.auto_save = False

    lc = { }
    for item in items:
        obj = get_object_by_name(props, item)
        for c in constraints:
            prop_name = "wfc_" + c
            if c in LIST_CONSTRAINTS:
                ilname = LIST_CONSTRAINTS[c]
                il = props.get(ilname, None)
                if il is None: continue
                if ilname not in lc: lc[ilname] = il
                idx=0
                while f"{prop_name}_{idx}" in obj:
                    del obj[f"{prop_name}_{idx}"]
                    idx+=1
            elif prop_name in obj:
                del obj[prop_name]
                props[c] = PROP_DEFAULTS[c]
            elif c.startswith("wfc_") and c in obj:
                del obj[c]
    for n in lc:
        c = getattr(props, n)
        c.clear()

    props.auto_save = auto_save

class WFC3D_OT_Update_Neighbor_Constraint(bpy.types.Operator):
    """Save neighbor constraints"""
    bl_idname = "object.wfc_update_neighbor_constraints"
    bl_label = "Save Neighbor(s)"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        update_neighbor_constraints(context.scene.wfc_props)
        self.report({'INFO'}, f"Neighbor constraints have been updated.")
        return {'FINISHED'}

class WFC3D_OT_Update_Connector_Constraint(bpy.types.Operator):
    """Save connector constraints"""
    bl_idname = "object.wfc_update_connector_constraints"
    bl_label = "Save Connector"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        update_connector_constraints(context.scene.wfc_props)
        self.report({'INFO'}, f"Connector constraints has been updated.")
        return {'FINISHED'}

class WFC3D_OT_Update_Grid_Constraints(bpy.types.Operator):
    """Save grid constraints"""
    bl_idname = "object.wfc_update_grid_constraints"
    bl_label = "Save Grid Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = ", ".join(get_selected_items(props.obj_list))
        update_grid_constraints(props)
        self.report({'INFO'}, f"Grid constraints of object(s) {obj_name} have been saved.")
        return {'FINISHED'}

class WFC3D_OT_UpdateConstraints(bpy.types.Operator):
    """Update constraints"""
    bl_idname = "object.wfc_update_constraints"
    bl_label = "Save Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        update_constraints(props, get_constraints(props))
        self.report({'INFO'}, f"{props.edit_constraints.capitalize()} constraints have been saved.")
        return {'FINISHED'}


class WFC3D_OT_ResetConstraints(bpy.types.Operator):
    """Reset constraints"""
    bl_idname = "object.wfc_reset_constraints"
    bl_label = "Reset"
    bl_description = "Reset constraints"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        _reset_constraints(props, get_constraints(props))
        update_edit_form(props, context)
        self.report({'INFO'}, f"{props.edit_constraints.capitalize()} constraints have been reset.")
        return {'FINISHED'}


class WFC3D_OT_SelectDropdownObject(bpy.types.Operator):
    """Select objects in 3D Viewport"""
    bl_idname = "object.wfc_select_dropdown_object"
    bl_label = ""
    list_name : bpy.props.StringProperty()
    def execute(self, context):
        props = context.scene.wfc_props
        sel_items = get_selected_items(getattr(props, self.list_name))
        if len(sel_items) > 0:
            obj = get_object_by_name(props, sel_items[0])
        else:
            self.report({'WARNING'}, "Please select an object in the object list.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for item in get_selected_items(getattr(props, self.list_name)):
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

class WFC3D_OT_GetSelectedObject(bpy.types.Operator):
    """Select objects selected in 3D Viewport"""
    bl_idname = "object.wfc_get_selected_object"
    bl_label = ""
    list_name: bpy.props.StringProperty()
    def execute(self, context):
        props = context.scene.wfc_props
        selected_objects = bpy.context.selected_objects

        if selected_objects:
            selected_object_names = [obj.name for obj in selected_objects]
            for obj in selected_objects:
                for child in props.collection_obj.children:
                    if obj.name in child.objects:
                        selected_object_names.append(child.name)
            for item in getattr(props, self.list_name):
                item.selected = item.obj.name in selected_object_names
            props.obj_list_idx = -1
        else:
            self.report({'WARNING'}, "No active object found")
            return {'CANCELLED'}
        return {'FINISHED'}


class WFC3D_OT_UpdateCollectionList(bpy.types.Operator):
    """Reload object list"""
    bl_idname = "collection.wfc_update_collection_list"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        handle_update_collection(self, context)
        return {'FINISHED'}


class WFC3D_OT_GenericListSelectAll(bpy.types.Operator):
    """Select all entries in the list"""
    bl_idname = "object.wfc_list_select_all"
    bl_label = ""
    list_name: bpy.props.StringProperty()
    def execute(self, context):
        set_select_all_list_items(getattr(context.scene.wfc_props, self.list_name), True)
        return {'FINISHED'}

class WFC3D_OT_GenericListSelectNone(bpy.types.Operator):
    """Deselect all entries in the list"""
    bl_idname = "object.wfc_list_select_none"
    bl_label = ""
    list_name : bpy.props.StringProperty()
    def execute(self, context):
        set_select_all_list_items(getattr(context.scene.wfc_props, self.list_name), False)
        return {'FINISHED'}


class WFC3D_OT_AutoSaveToggle(bpy.types.Operator):
    """Auto save toggle"""
    bl_idname = "collection.wfc_auto_save_toggle"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        props.auto_save = not props.auto_save
        return {'FINISHED'}

class WFC3D_OT_InfoToggle(bpy.types.Operator):
    """Show/Hide Constraints Information"""
    bl_idname = "collection.wfc_info_toggle"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        props.info_toggle = not props.info_toggle
        return {'FINISHED'}

class WFC3DVisDirections(bpy.types.Operator):
    """Show directions"""
    bl_idname = "object.wfc_vis_directions"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        props.vis_directions = not props.vis_directions
        for item in get_selected_items(props.obj_list):
            obj = get_object_by_name(props, item)
            if props.vis_directions:
                props.vis_directions = add_directions_geometry_nodegroup(obj)
            else:
                remove_directions_geometry_nodegroup(obj)

        return {'FINISHED'}

class WFC3D_OT_GenericRemoveListItems(bpy.types.Operator):
    """Remove selected constraint items from list"""
    bl_idname = "object.wfc_generic_remove_list_items"
    bl_label = ""
    bl_description = "Remove selected constraint items from list"
    def execute(self, context):
        props = context.scene.wfc_props
        constraints = get_constraints(props)
        lst = getattr(props, LIST_CONSTRAINTS[constraints[0]])
        selected_indices = [i for i, item in enumerate(lst) if item.selected]
        for idx in sorted(selected_indices, reverse=True):
            lst.remove(idx)
        update_constraints(props, constraints)
        return {'FINISHED'}

class WFC3D_OT_GenericAddListItem(bpy.types.Operator):
    """Add new constraint item to list"""
    bl_idname = "object.wfc_generic_add_list_item"
    bl_label = ""
    bl_description = "Add new constraint item to list"
    def execute(self, context):
        props = context.scene.wfc_props
        constraints = get_constraints(props)
        item = None
        for c in constraints:
            if c not in LIST_CONSTRAINTS: continue
            if item is None:
                lst = getattr(props, LIST_CONSTRAINTS[c])
                item = lst.add()
            setattr(item, c, PROP_DEFAULTS[c])
        return {'FINISHED'}
class WFC3D_OT_GenericDuplicateListItems(bpy.types.Operator):
    bl_idname = "object.wfc_generic_duplicate_selected_items"
    bl_label = ""
    bl_description = "Duplicate selected constraints"
    def execute(self, context):
        props = context.scene.wfc_props
        constraints = get_constraints(props)
        lst = getattr(props, LIST_CONSTRAINTS[constraints[0]])
        item = None
        sel_items = [ item for item in lst if item.selected]
        for si in sel_items:
            item = lst.add()
            for c in constraints:
                setattr(item, c, getattr(si,c))
        return {'FINISHED'}
class WFC3D_OT_OpenWebLink(bpy.types.Operator):
    """Open Web Link"""
    bl_idname = "object.wfc_open_web_link"
    bl_label = ""
    bl_description = "Open Online Help on GitHub"
    url : bpy.props.StringProperty(name="URL")
    def execute(self, context):
        import webbrowser
        webbrowser.open(self.url)
        return {'FINISHED'}

class WFC3D_OT_ResetAllConstraints(bpy.types.Operator):
    """Reset all constraints"""
    bl_idname = "object.wfc_reset_all_constraints"
    bl_label = "Reset All"
    bl_description = "Reset all constraints"
    bl_options = {'REGISTER', 'UNDO'}
    sure : bpy.props.BoolProperty(name="I'm sure!", default=False)
    def execute(self, context):
        props = context.scene.wfc_props
        if not self.sure: return {'CANCELLED'}
        # remove default objects and  wfc_-Properties
        for obj in props.collection_obj.objects:
            if obj.name.startswith(get_default_empty_name()):
                bpy.data.objects.remove(obj, do_unlink=True)
                continue
            for p in obj.keys():
                if not p.startswith("wfc_"): continue
                del obj[p]
        for child in props.collection_obj.children:
            for obj in child.objects:
                if obj.name.startswith(get_default_empty_name()):
                    bpy.data.objects.remove(obj, do_unlink=True)
                    break
        self.report({'INFO'}, "All WFC3D Generator constraints have been reset.")
        props.reset_all_confirmation = False
        return {'FINISHED'}



operators = [
    WFC3D_OT_ResetAllConstraints,
    WFC3D_OT_GenericListSelectAll,
    WFC3D_OT_GenericListSelectNone,
    WFC3D_OT_OpenWebLink,
    WFC3D_OT_GenericDuplicateListItems,
    WFC3D_OT_GenericAddListItem,
    WFC3D_OT_GenericRemoveListItems,
    WFC3D_OT_InfoToggle,
    WFC3D_OT_AutoSaveToggle,
    WFC3D_OT_Update_Neighbor_Constraint,
    WFC3D_OT_Update_Connector_Constraint,
    WFC3D_OT_Update_Grid_Constraints,
    WFC3D_OT_UpdateConstraints,
    WFC3D_OT_ResetConstraints,
    WFC3D_OT_SelectDropdownObject,
    WFC3D_OT_GetSelectedObject,
    WFC3D_OT_UpdateCollectionList,
    WFC3DVisDirections,
]
