import bpy

from .constants import *
from .properties import update_constraint_properties, handle_update_collection
from .helper import get_default_empty_object

def _get_obj(props, name):
    collection = props.collection_obj
    if props.edit_type == 'objects':
        if name in collection.objects:
            return collection.objects[name]
        elif name in collection.children:
            return get_default_empty_object(collection.children[name], True)
    elif props.edit_type == 'defaults':
        return get_default_empty_object(collection, True)
    return None


def _get_selected_items(obj_list):
    return [item.name for item in obj_list if item.selected]


def _get_obj_list(props):
    return ",".join(_get_selected_items(props.obj_list))


def _update_constraints(props, constraints):
    items = []
    if props.edit_type == 'objects':
        items = _get_selected_items(props.obj_list)
    elif props.edit_type == 'defaults':
        items = [DEFAULT_EMPTY_NAME]

    for item in items:
        obj = _get_obj(props, item)
        for c in constraints:
            if c in props:
                if props[c] != PROP_DEFAULTS[c]:
                    obj["wfc_" + c] = props[c]
                elif "wfc_" + c in obj:
                    del obj["wfc_" + c]


def _reset_constraints(props, constraints):
    items = []
    if props.edit_type == 'objects':
        items = _get_selected_items(props.obj_list)
    elif props.edit_type == 'defaults':
        items = [DEFAULT_EMPTY_NAME]

    for item in items:
        obj = _get_obj(props, item)
        for c in constraints:
            if "wfc_" + c in obj:
                del obj["wfc_" + c]
                props[c] = PROP_DEFAULTS[c]
            elif c.startswith("wfc_") and c in obj:
                del obj[c]


class COLLECTION_OT_WFC3DUpdate_Neighbor_Constraint(bpy.types.Operator):
    """Save neighbor constraints"""
    bl_idname = "object.wfc_update_neighbor_constraints"
    bl_label = "Save Neighbor(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def _set_neighbors(self, obj, prop_name, neighbors):
        n = ",".join(neighbors)
        obj[prop_name] = n
        self.report({'INFO'}, f"Neighbor(s) {n} has/have been added to {prop_name} of object {obj.name}")

    def execute(self, context):
        props = context.scene.wfc_props
        prop_name = props.edit_neighbor_constraint
        if props.no_neighbor_allowed:
            neighbors = ["-"]
        else:
            neighbors = [item.value for item in props.neighbor_list if item.selected]
        if props.edit_type == 'objects':
            for item in _get_selected_items(props.obj_list):
                obj = _get_obj(props, item)
                _update_constraints(props, ADD_NEIGHBOR_CONSTRAINTS)
                self._set_neighbors(obj, prop_name, neighbors)
        elif props.edit_type == 'defaults':
            obj = _get_obj(props, DEFAULT_EMPTY_NAME)
            _update_constraints(props, ADD_NEIGHBOR_CONSTRAINTS)
            self._set_neighbors(obj, prop_name, neighbors)
        return {'FINISHED'}


class COLLECTION_OT_WFC3DUpdate_Grid_Constraints(bpy.types.Operator):
    """Save grid constraints"""
    bl_idname = "object.wfc_update_grid_constraints"
    bl_label = "Save Grid Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    def _get_new_prop_val(self, props, prop_name, values):
        newval = []
        if prop_name + "_none" in props and props[prop_name + "_none"]:
            newval.append("-")
        else:
            for v in values:
                if props[prop_name + "_" + v]:
                    newval.append(v)
        return ",".join(newval)

    def _set_grid_constraints(self, obj, props):
        obj["wfc_corners"] = self._get_new_prop_val(props, "corner",
                                                    ['fbl', 'fbr', 'ftl', 'ftr', 'bbl', 'bbr', 'btl', 'btr'])
        obj["wfc_edges"] = self._get_new_prop_val(props, "edge",
                                                  ['fb', 'fl', 'fr', 'ft', 'bb', 'bl', 'br', 'bt', 'lb', 'lt', 'rb',
                                                   'rt'])
        obj["wfc_faces"] = self._get_new_prop_val(props, "face", ['front', 'back', 'top', 'bottom', 'left', 'right'])
        if props["inside_none"]:
            obj["wfc_inside"] = "-"
        else:
            obj["wfc_inside"] = ""

    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = ", ".join(_get_selected_items(props.obj_list))
        if props.edit_type == 'objects':
            for item in _get_selected_items(props.obj_list):
                self._set_grid_constraints(_get_obj(props, item), props)
        elif props.edit_type == 'defaults':
            self._set_grid_constraints(_get_obj(props, DEFAULT_EMPTY_NAME), props)

        self.report({'INFO'}, f"Grid constraints of object(s) {obj_name} have been saved.")
        return {'FINISHED'}


def _get_constraints(props):
    constraints = []
    if props.edit_constraints == 'symmetry':
        constraints = SYMMETRY_CONSTRAINTS
    elif props.edit_constraints == 'frequency':
        constraints = FREQUENCY_CONSTRAINTS
    elif props.edit_constraints == 'transformation':
        constraints = TRANSFORMATION_CONSTRAINTS
    elif props.edit_constraints == 'probability':
        constraints = PROBABILITY_CONSTRAINTS
    elif props.edit_constraints == 'region':
        constraints = REGION_CONSTRAINTS
    elif props.edit_constraints == 'grid':
        constraints = GRID_CONSTRAINTS
    elif props.edit_constraints == 'neighbor':
        constraints = [props.edit_neighbor_constraint]
    return constraints


class COLLECTION_OT_WFC3DUpdateConstraints(bpy.types.Operator):
    """Update constraints"""
    bl_idname = "object.wfc_update_constraints"
    bl_label = "Save Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _update_constraints(props, _get_constraints(props))
        self.report({'INFO'}, f"{props.edit_constraints.capitalize()} constraints of {obj_list} have been saved.")
        return {'FINISHED'}


class COLLECTION_OT_WFC3DResetConstraints(bpy.types.Operator):
    """Reset constraints"""
    bl_idname = "object.wfc_reset_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _reset_constraints(props, _get_constraints(props))
        update_constraint_properties(props, context)
        self.report({'INFO'}, f"{props.edit_constraints.capitalize()} constraints of {obj_list} have been reset.")
        return {'FINISHED'}


class COLLECTION_OT_WFC3DSelectDropdownObject(bpy.types.Operator):
    """Select objects in 3D Viewport"""
    bl_idname = "collection.wfc_select_dropdown_object"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        sel_items = _get_selected_items(props.obj_list)
        if len(sel_items) > 0:
            obj = _get_obj(props, sel_items[0])
        else:
            self.report({'WARNING'}, "Please select an object in the object list.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for item in _get_selected_items(props.obj_list):
            _get_obj(props, item).select_set(True)

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


class COLLECTION_OT_WFC3DSelectNeighborObject(bpy.types.Operator):
    """Select objects in 3D Viewport"""
    bl_idname = "collection.wfc_select_neighbor_object"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        sel_items = _get_selected_items(props.neighbor_list)
        if len(sel_items) > 0:
            obj = _get_obj(props, sel_items[0])
        else:
            self.report({'WARNING'}, "Please select an object in the object list.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for item in _get_selected_items(props.neighbor_list):
            _get_obj(props, item).select_set(True)

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


class COLLECTION_OT_WFC3DGetSelectedObject(bpy.types.Operator):
    """Select objects selected in 3D Viewport"""
    bl_idname = "collection.wfc_get_selected_object"
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
            for item in props.obj_list:
                item.selected = item.name in selected_object_names
            props.obj_list_idx = -1
        else:
            self.report({'WARNING'}, "No active object found")
            return {'CANCELLED'}
        return {'FINISHED'}


class COLLECTION_OT_WFC3DGetNeighborSelectedObject(bpy.types.Operator):
    """Select objects selected in 3D Viewport"""
    bl_idname = "collection.wfc_get_neighbor_selected_object"
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
            for item in props.neighbor_list:
                item.selected = item.value in selected_object_names
            props.neighbor_list_idx = -1
        else:
            self.report({'WARNING'}, "No active object found")
            return {'CANCELLED'}
        return {'FINISHED'}


class COLLECTION_OT_WFC3DUpdateCollectionList(bpy.types.Operator):
    """Reload object list"""
    bl_idname = "collection.wfc_update_collection_list"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        handle_update_collection(self, context)
        return {'FINISHED'}


def set_select_all_list_items(itemlist, selected):
    for item in itemlist:
        item.selected = selected


class COLLECTION_OT_WFC3DCollectionListSelectAll(bpy.types.Operator):
    """Select all objects in list"""
    bl_idname = "collection.wfc_collection_list_select_all"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.obj_list, True)
        return {'FINISHED'}


class COLLECTION_OT_WFC3DCollectionListSelectNone(bpy.types.Operator):
    """Deselect all objects in list"""
    bl_idname = "collection.wfc_collection_list_select_none"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.obj_list, False)
        return {'FINISHED'}


class COLLECTION_OT_WFC3DNeighborListSelectAll(bpy.types.Operator):
    """Select all objects in list"""
    bl_idname = "collection.wfc_neighbor_list_select_all"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.neighbor_list, True)
        return {'FINISHED'}


class COLLECTION_OT_WFC3DNeighborListSelectNone(bpy.types.Operator):
    """Deselect all objects in list"""
    bl_idname = "collection.wfc_neighbor_list_select_none"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.neighbor_list, False)
        return {'FINISHED'}


operators = [
    COLLECTION_OT_WFC3DUpdate_Neighbor_Constraint,
    COLLECTION_OT_WFC3DUpdate_Grid_Constraints,
    COLLECTION_OT_WFC3DUpdateConstraints,
    COLLECTION_OT_WFC3DResetConstraints,
    COLLECTION_OT_WFC3DSelectDropdownObject,
    COLLECTION_OT_WFC3DGetSelectedObject,
    COLLECTION_OT_WFC3DGetNeighborSelectedObject,
    COLLECTION_OT_WFC3DSelectNeighborObject,
    COLLECTION_OT_WFC3DUpdateCollectionList,
    COLLECTION_OT_WFC3DCollectionListSelectAll,
    COLLECTION_OT_WFC3DCollectionListSelectNone,
    COLLECTION_OT_WFC3DNeighborListSelectAll,
    COLLECTION_OT_WFC3DNeighborListSelectNone,
]
