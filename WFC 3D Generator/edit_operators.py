import bpy

from .constants import *
from .properties import update_constraint_properties, handle_update_collection, handle_edit_neighbor_constraint_update

def _get_obj(collection, name):
    if name in collection.objects:
        return collection.objects[name]
    elif name in collection.children:
        return collection.children[name].objects[0]
    
def _get_selected_items(obj_list):
    return [ item.name for item in obj_list if item.selected]

def _get_obj_list(props):
    return ",".join(_get_selected_items(props.obj_list))

def _update_constraints(props, constraints):
    for item in _get_selected_items(props.obj_list):
        obj = _get_obj(props.collection_obj, item)
        for c in constraints:
            if c in props:
                if props[c] != PROP_DEFAULTS[c]:
                    obj["wfc_"+c] = props[c]
                else:
                    if "wfc_"+c in obj:
                        del obj["wfc_"+c]

def _reset_constraints(props, constraints):
    for item in _get_selected_items(props.obj_list):
        obj = _get_obj(props.collection_obj, item)
        for c in constraints:
            if "wfc_"+c in obj:
                del obj["wfc_" +c]
                props[c] = PROP_DEFAULTS[c]
            
class COLLECTION_OT_WFC3DUpdate_Neighbor_Constraint(bpy.types.Operator):
    """Save neighbor constraints"""
    bl_idname = "object.wfc_update_constraint"
    bl_label = "Save Neighbor(s)"
    bl_options = {'REGISTER', 'UNDO'}
    def _set_neighbors(self, obj, prop_name, neighbors):
        obj[prop_name] = neighbors
        self.report({'INFO'}, f"Neighbor(s) {neighbors} has/have been added to {prop_name} of object {obj.name}")
    def execute(self, context):
        props= context.scene.wfc_props
        prop_name = props.edit_neighbor_constraint
        if props.no_neighbor_allowed:
            neighbors = ["-"]
        else:
            neighbors = [ item.value for item in props.neighbor_list if item.selected ]
        for item in _get_selected_items(props.obj_list):
            self._set_neighbors(_get_obj(props.collection_obj, item), prop_name, ",".join(neighbors))
        return {'FINISHED'}

    
class COLLECTION_OT_WFC3DReset_Neighbor_Constraint(bpy.types.Operator):
    """Reset selected neighbor constraints"""
    bl_idname = "object.wfc_reset_constraint"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def _reset_neighbor(self, obj, prop_name):
        if prop_name and prop_name in obj:
            obj[prop_name]=''
            self.report({'INFO'}, f"{prop_name} have been reset for object: {obj.name}")

    def execute(self, context):
        props = context.scene.wfc_props
        prop_name = props.edit_neighbor_constraint
        for item in _get_selected_items(props.obj_list):
            self._reset_neighbor(_get_obj(props.collection_obj, item), prop_name)
        handle_edit_neighbor_constraint_update(self,context)
        return {'FINISHED'}

class COLLECTION_OT_WFC3DUpdate_Grid_Constraints(bpy.types.Operator):
    """Save grid constraints"""
    bl_idname = "object.wfc_update_grid_constraints"
    bl_label = "Save Grid Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def _get_new_prop_val(self, props, prop_name, values):
        newval = []
        if prop_name+"_none" in props and props[prop_name+"_none"]:
            newval.append("-")
        else:
            for v in values:
                if props[prop_name+"_"+v]:
                    newval.append(v)
        return ",".join(newval)
    
    def _set_grid_constraints(self, obj, props):
        obj["wfc_corners"]= self._get_new_prop_val(props, "corner",['fbl','fbr','ftl','ftr','bbl','bbr','btl','btr'])
        obj["wfc_edges"] = self._get_new_prop_val(props, "edge",['fb','fl','fr','ft','bb','bl','br','bt','lb','lt','rb','rt'])
        obj["wfc_faces"] = self._get_new_prop_val(props, "face",['front','back','top','bottom','left','right'])
        if props["inside_none"]:
            obj["wfc_inside"] = "-"
        else:
            obj["wfc_inside"] = ""
                
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = ", ".join(_get_selected_items(props.obj_list))
        for item in _get_selected_items(props.obj_list):
            self._set_grid_constraints(_get_obj(props.collection_obj, item), props)
        
        self.report({'INFO'}, f"Grid constraints of object(s) {obj_name} have been saved.")
        return {'FINISHED'}

class COLLECTION_OT_WFC3DReset_Grid_Constraints(bpy.types.Operator):
    """Reset grid constraints"""
    bl_idname = "object.wfc_reset_grid_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _reset_constraints(props, GRID_CONSTRAINTS)
        update_constraint_properties(props, context)
        self.report({'INFO'}, f"Grid constraints of {obj_list} have been reset.")  
        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Region_Constraints(bpy.types.Operator):
    """Save region constraints"""
    bl_idname = "object.wfc_update_region_constraints"
    bl_label = "Save Region Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _update_constraints(props, REGION_CONSTRAINTS)
        self.report({'INFO'}, f"Region constraints of {obj_list} have been saved.")
        return {'FINISHED'}

class COLLECTION_OT_WFC3DReset_Region_Constraints(bpy.types.Operator):
    """Reset region constraints"""
    bl_idname = "object.wfc_reset_region_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _reset_constraints(props, REGION_CONSTRAINTS)
        update_constraint_properties(props, context)
        self.report({'INFO'}, f"Region constraints of {obj_list} have been reset.")  
        return {'FINISHED'}
    
class COLLECTION_OT_WFC3DUpdate_Probability_Constraints(bpy.types.Operator):
    """Save probability constraints"""
    bl_idname = "object.wfc_update_probability_constraints"
    bl_label = "Save Probability Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _update_constraints(props, PROBABILITY_CONSTRAINTS)
        self.report({'INFO'}, f"Probability constraints of {obj_list} have been saved.")
        return {'FINISHED'}

class COLLECTION_OT_WFC3DReset_Probability_Constraints(bpy.types.Operator):
    """Reset probability constraints"""
    bl_idname = "object.wfc_reset_probability_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _reset_constraints(props, PROBABILITY_CONSTRAINTS)
        update_constraint_properties(props, context)
        self.report({'INFO'}, f"Probability constraints of {obj_list} have been reset.")  
        return {'FINISHED'}


class COLLECTION_OT_WFC3DUpdate_Frequency_Constraints(bpy.types.Operator):
    """Save frequency constraints"""
    bl_idname = "object.wfc_update_frequency_constraints"
    bl_label = "Save Frequency Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _update_constraints(props, FREQUENCY_CONSTRAINTS)
        self.report({'INFO'}, f"Frequency constraints of {obj_list} have been saved.")  
        return {'FINISHED'}

class COLLECTION_OT_WFC3DReset_Frequency_Constraints(bpy.types.Operator):
    """Reset frequency constraints"""
    bl_idname = "object.wfc_reset_frequency_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _reset_constraints(props, FREQUENCY_CONSTRAINTS)
        update_constraint_properties(props, context)
        self.report({'INFO'}, f"Frequency constraints of {obj_list} have been reset.")  
        return {'FINISHED'}

class COLLECTION_OT_WFC3DUpdate_Transformation_Constraints(bpy.types.Operator):
    """Save transformation constraints"""
    bl_idname = "object.wfc_update_transformation_constraints"
    bl_label = "Save Transformation Constraints"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _update_constraints(props, TRANSFORMATION_CONSTRAINTS)         
        self.report({'INFO'}, f"Transformation constraints of {obj_list} have been saved.")  
        return {'FINISHED'}
    
class COLLECTION_OT_WFC3DReset_Transformation_Constraints(bpy.types.Operator):
    """Reset transformation constraints"""
    bl_idname = "object.wfc_reset_transformation_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _reset_constraints(props, TRANSFORMATION_CONSTRAINTS)
        update_constraint_properties(props, context)
        self.report({'INFO'}, f"Transformation constraints of {obj_list} have been reset.")  
        return {'FINISHED'}
    
class COLLECTION_OT_WFC3DUpdate_Symmetry_Constraints(bpy.types.Operator):
    """Update symmetry constraints"""
    bl_idname = "object.wfc_update_symmetry_constraints"
    bl_label = "Save Symmetry Constraints"
    bl_options = {'REGISTER','UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list  = _get_obj_list(props)
        _update_constraints(props, SYMMETRY_CONSTRAINTS)
        self.report({'INFO'}, f"Symmetry constraints of {obj_list} have been saved.")
        return {'FINISHED'}
 
class COLLECTION_OT_WFC3DReset_Symmetry_Constraints(bpy.types.Operator):
    """Reset symmetry constraints"""
    bl_idname = "object.wfc_reset_symmetry_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_list = _get_obj_list(props)
        _reset_constraints(props, SYMMETRY_CONSTRAINTS)
        update_constraint_properties(props, context)
        self.report({'INFO'}, f"Symmetry constraints of {obj_list} have been reset.")  
        return {'FINISHED'}
    
class COLLECTION_OT_WFC3DSelectDropdownObject(bpy.types.Operator):
    """Select objects in 3D Viewport"""
    bl_idname = "collection.wfc_select_dropdown_object"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        collection = props.collection_obj
        sel_items = _get_selected_items(props.obj_list)
        if len(sel_items)>0:
            obj = _get_obj(props.collection_obj, sel_items[0]) 
        else:
            self.report({'WARNING'}, "Please select an object in the object list.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for item in _get_selected_items(props.obj_list):
            _get_obj(props.collection_obj, item).select_set(True)
        
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
        collection = props.collection_obj
        sel_items = _get_selected_items(props.neighbor_list)
        if len(sel_items)>0:
            obj = _get_obj(props.collection_obj, sel_items[0]) 
        else:
            self.report({'WARNING'}, "Please select an object in the object list.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for item in _get_selected_items(props.neighbor_list):
            _get_obj(props.collection_obj, item).select_set(True)
        
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
    bl_options = {'REGISTER','UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        selected_objects = bpy.context.selected_objects
        
        if selected_objects:
            selected_object_names = [ obj.name for obj in selected_objects ]
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
            selected_object_names = [ obj.name for obj in selected_objects ]
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
    bl_options = {'REGISTER','UNDO'}
    def execute(self,context):
        handle_update_collection(self,context)
        return {'FINISHED'}

def set_select_all_list_items(list, selected):
    for item in list:
        item.selected = selected
        
class COLLECTION_OT_WFC3DCollectionListSelectAll(bpy.types.Operator):
    """Select all objects in list"""
    bl_idname = "collection.wfc_collection_list_select_all"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}
    def execute(self,context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.obj_list, True)
        return {'FINISHED'}

class COLLECTION_OT_WFC3DCollectionListSelectNone(bpy.types.Operator):
    """Deselect all objects in list"""
    bl_idname = "collection.wfc_collection_list_select_none"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}
    def execute(self,context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.obj_list, False)
        return {'FINISHED'}
class COLLECTION_OT_WFC3DNeighborListSelectAll(bpy.types.Operator):
    """Select all objects in list"""
    bl_idname = "collection.wfc_neighbor_list_select_all"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}
    def execute(self,context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.neighbor_list, True)
        return {'FINISHED'}

class COLLECTION_OT_WFC3DNeighborListSelectNone(bpy.types.Operator):
    """Deselect all objects in list"""
    bl_idname = "collection.wfc_neighbor_list_select_none"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}
    def execute(self,context):
        props = context.scene.wfc_props
        set_select_all_list_items(props.neighbor_list, False)
        return {'FINISHED'}



operators = [
    COLLECTION_OT_WFC3DUpdate_Neighbor_Constraint,
    COLLECTION_OT_WFC3DReset_Neighbor_Constraint,
    COLLECTION_OT_WFC3DUpdate_Grid_Constraints,
    COLLECTION_OT_WFC3DReset_Grid_Constraints,
    COLLECTION_OT_WFC3DUpdate_Region_Constraints,
    COLLECTION_OT_WFC3DReset_Region_Constraints,
    COLLECTION_OT_WFC3DUpdate_Probability_Constraints,
    COLLECTION_OT_WFC3DReset_Probability_Constraints,
    COLLECTION_OT_WFC3DUpdate_Frequency_Constraints,
    COLLECTION_OT_WFC3DReset_Frequency_Constraints,
    COLLECTION_OT_WFC3DUpdate_Transformation_Constraints,
    COLLECTION_OT_WFC3DReset_Transformation_Constraints,
    COLLECTION_OT_WFC3DUpdate_Symmetry_Constraints,
    COLLECTION_OT_WFC3DReset_Symmetry_Constraints,
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
