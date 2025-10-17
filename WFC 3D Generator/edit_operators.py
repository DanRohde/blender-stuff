import bpy

from .constants import PROP_DEFAULTS, FREQUENCY_CONSTRAINTS, TRANSFORMATION_CONSTRAINTS

from .properties import update_constraint_properties, handle_update_collection, handle_edit_neighbor_constraint_update

def _get_obj(collection, name):
    if name in collection.objects:
        return collection.objects[name]
    elif name in collection.children:
        return collection.children[name].objects[0]
    
def _get_selected_items(obj_list):
    return [ item.name for item in obj_list if item.selected]

class COLLECTION_OT_WFC3DSave_Neighbor_Constraint(bpy.types.Operator):
    """Save neighbor constraints"""
    bl_idname = "object.wfc_save_constraint"
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
    def _reset_grid(self, obj):
        for c in ["corners","edges","faces","inside"]:
            obj["wfc_"+c] = PROP_DEFAULTS[c]
        
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = ", ".join(_get_selected_items(props.obj_list))
        for item in _get_selected_items(props.obj_list):
            self._reset_grid(_get_obj(props.collection_obj, item))
        
        update_constraint_properties(props, context)
        
        self.report({'INFO'}, f"Grid constraints of object(s) {obj_name} have been reset.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Probability_Constraints(bpy.types.Operator):
    """Save probability constraints"""
    bl_idname = "object.wfc_update_probability_constraints"
    bl_label = "Save Probability Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def _update_prob(self, obj, props):
        obj["wfc_weight"] = props.weight
        obj["wfc_probability"] = props.probability
        
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = ",".join(_get_selected_items(props.obj_list))
        for item in _get_selected_items(props.obj_list):
            self._update_prob(_get_obj(props.collection_obj, item), props)
            
        self.report({'INFO'}, f"Probability constraints of object(s) {obj_name} have been saved.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Frequency_Constraints(bpy.types.Operator):
    """Save frequency constraints"""
    bl_idname = "object.wfc_update_frequency_constraints"
    bl_label = "Save Frequency Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def _update(self, obj, props):
        for c in FREQUENCY_CONSTRAINTS:
            obj["wfc_"+c] = props.get(c,PROP_DEFAULTS[c])
        
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = ",".join(_get_selected_items(props.obj_list))
        for item in _get_selected_items(props.obj_list):
            self._update(_get_obj(props.collection_obj, item), props)

        self.report({'INFO'}, f"Frequency constraints of object(s) {obj_name} have been saved.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DReset_Frequency_Constraints(bpy.types.Operator):
    """Reset frequency constraints"""
    bl_idname = "object.wfc_reset_frequency_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def _reset(self, obj):
        for c in FREQUENCY_CONSTRAINTS:
            obj["wfc_"+c] = PROP_DEFAULTS[c]
        
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = ",".join(_get_selected_items(props.obj_list))
        for item in _get_selected_items(props.obj_list):
            self._reset(_get_obj(props.collection_obj, item))
        update_constraint_properties(props, context)
        
        self.report({'INFO'}, f"Frequency constraints of object(s) {obj_name} have been reset.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Transformation_Constraints(bpy.types.Operator):
    """Save transformation constraints"""
    bl_idname = "object.wfc_update_transformation_constraints"
    bl_label = "Save Transformation Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def _update(self, obj, props):
        for c in TRANSFORMATION_CONSTRAINTS:
            if c in props and props[c] != PROP_DEFAULTS[c]:
                obj["wfc_"+c] = props[c]
        
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = ",".join(_get_selected_items(props.obj_list))
        for item in _get_selected_items(props.obj_list):
            self._update(_get_obj(props.collection_obj, item), props)
            
        self.report({'INFO'}, f"Transformation constraints of object(s) {obj_name} have been saved.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DReset_Transformation_Constraints(bpy.types.Operator):
    """ Reset transformation constraints. """
    bl_idname = "object.wfc_reset_transformation_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def _reset(self,obj, props):
        for c in TRANSFORMATION_CONSTRAINTS:
            if "wfc_"+c in obj:
                del obj["wfc_" +c]
            props[c] = PROP_DEFAULTS[c]
        
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = ",".join(_get_selected_items(props.obj_list))
        for item in _get_selected_items(props.obj_list):
            self._reset(_get_obj(props.collection_obj, item), props)
             
        self.report({'INFO'}, f"Transformation constraints of object {obj_name} have been reset.")  

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
    COLLECTION_OT_WFC3DSave_Neighbor_Constraint,
    COLLECTION_OT_WFC3DReset_Neighbor_Constraint,
    COLLECTION_OT_WFC3DUpdate_Grid_Constraints,
    COLLECTION_OT_WFC3DReset_Grid_Constraints,
    COLLECTION_OT_WFC3DUpdate_Probability_Constraints,
    COLLECTION_OT_WFC3DUpdate_Frequency_Constraints,
    COLLECTION_OT_WFC3DReset_Frequency_Constraints,
    COLLECTION_OT_WFC3DUpdate_Transformation_Constraints,
    COLLECTION_OT_WFC3DReset_Transformation_Constraints,
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
