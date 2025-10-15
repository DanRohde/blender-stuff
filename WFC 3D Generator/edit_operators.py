import bpy

from .constants import PROP_DEFAULTS

from .properties import update_constraint_properties

class COLLECTION_OT_WFC3DAdd_Neighbor_Constraint(bpy.types.Operator):
    """ Add neighbor constraints """
    bl_idname = "object.wfc_add_constraint"
    bl_label = "Add Neighbor"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props= context.scene.wfc_props
        obj_name = props.edit_object
        prop_name = props.edit_neighbor_constraint
        neighbor = props.select_neighbor
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name][0]
        else:
            obj = bpy.data.objects[obj_name]
        if prop_name in obj:
            if obj[prop_name] == "":
                l = []
            else:
                if obj[prop_name] == "-":
                    l = []
                else: 
                    l = obj[prop_name].split(",")
            if neighbor not in l:
                if neighbor == '-':
                    l = []
                l.append(neighbor)
                obj[prop_name]=",".join(l)
                self.report({'INFO'}, f"Neighbor {neighbor} has been added to {prop_name} of object {obj_name}")  
            else:
                self.report({'WARNING'}, f"Neighbor {neighbor} is already in {prop_name} of object {obj_name}")
        else:
            obj[prop_name] = neighbor
        return {'FINISHED'}

        
class COLLECTION_OT_WFC3DRemove_Neighbor_Constraint(bpy.types.Operator):
    """ Remove neighbor constraints """
    bl_idname = "object.wfc_remove_constraint"
    bl_label = "Remove Neighbor"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props= context.scene.wfc_props
        obj_name = props.edit_object
        prop_name = props.edit_neighbor_constraint
        neighbor = props.select_neighbor
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name][0]
        else:
            obj = bpy.data.objects[obj_name]
        
        if prop_name in obj:
            if obj[prop_name] == "" or obj[prop_name] == neighbor:
                obj[prop_name] = ""
            else:
                l = [n for n in obj[prop_name].split(",") if n != neighbor ]
                obj[prop_name] = ",".join(l)
            self.report({'INFO'}, f"Neighbor {neighbor} has been removed from {prop_name} of object {obj_name}")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DReset_Neighbor_Constraint(bpy.types.Operator):
    """ Reset selected neighbor constraints """
    bl_idname = "object.wfc_reset_constraint"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props= context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name][0]
        else:
            obj = bpy.data.objects[obj_name]
        
        if props.edit_neighbor_constraint and props.edit_neighbor_constraint in obj:
            obj[props.edit_neighbor_constraint]=''
            self.report({'INFO'}, f"{props.edit_neighbor_constraint} have been reset for object: {obj_name}")

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
        
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
        
        obj["wfc_corners"]= self._get_new_prop_val(props, "corner",['fbl','fbr','ftl','ftr','bbl','bbr','btl','btr'])
        obj["wfc_edges"] = self._get_new_prop_val(props, "edge",['fb','fl','fr','ft','bb','bl','br','bt','lb','lt','rb','rt'])
        obj["wfc_faces"] = self._get_new_prop_val(props, "face",['front','back','top','bottom','left','right'])
        if props["inside_none"]:
            obj["wfc_inside"] = "-"
        else:
            obj["wfc_inside"] = ""
        
        self.report({'INFO'}, f"Grid constraints of object {obj_name} have been saved.")
        return {'FINISHED'}
class COLLECTION_OT_WFC3DReset_Grid_Constraints(bpy.types.Operator):
    """Reset grid constraints"""
    bl_idname = "object.wfc_reset_grid_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
        for c in ["corners","edges","faces","inside"]:
            obj["wfc_"+c] = PROP_DEFAULTS[c]
            
        update_constraint_properties(props, context)
        
        self.report({'INFO'}, f"Grid constraints of object {obj_name} have been reset.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Probability_Constraints(bpy.types.Operator):
    """Save probability constraints"""
    bl_idname = "object.wfc_update_probability_constraints"
    bl_label = "Save Probability Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
        
        obj["wfc_weight"] = props.weight
        obj["wfc_probability"] = props.probability
        
        self.report({'INFO'}, f"Probability constraints of object {obj_name} have been saved.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Frequency_Constraints(bpy.types.Operator):
    """Save frequency constraints"""
    bl_idname = "object.wfc_update_frequency_constraints"
    bl_label = "Save Frequency Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
        
        obj["wfc_freq_grid"] = props.freq_grid
        obj["wfc_freq_axles"] = props.freq_axles
        obj["wfc_freq_neighbor"] = props.freq_neighbor
        
        self.report({'INFO'}, f"Frequency constraints of object {obj_name} have been saved.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DReset_Frequency_Constraints(bpy.types.Operator):
    """Reset frequency constraints"""
    bl_idname = "object.wfc_reset_frequency_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
       
        for c in ["freq_grid","freq_neighbor","freq_axles"]:
            obj["wfc_"+c] = PROP_DEFAULTS[c]
            
        update_constraint_properties(props, context)
        
        self.report({'INFO'}, f"Frequency constraints of object {obj_name} have been reset.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DUpdate_Transformation_Constraints(bpy.types.Operator):
    """Save transformation constraints"""
    bl_idname = "object.wfc_update_transformation_constraints"
    bl_label = "Save Transformation Constraints"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
         
        for c in ["scale_min","scale_max","scale_steps","scale_type","scale_uni","rotation_min","rotation_max","rotation_steps",\
                  "translation_min","translation_max","translation_steps",\
                  "rotation_neighbor", "rotation_grid"]:
            if c in props:
                obj["wfc_"+c] = props[c]
            else:
                obj["wfc_"+c] = PROP_DEFAULTS[c]
         
        self.report({'INFO'}, f"Transformation constraints of object {obj_name} have been saved.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DReset_Transformation_Constraints(bpy.types.Operator):
    """ Reset transformation constraints. """
    bl_idname = "object.wfc_reset_transformation_constraints"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.edit_object
        
        if obj_name in bpy.data.collections:
            obj = bpy.data.collections[obj_name].objects[0]
        else:
            obj = bpy.data.objects[obj_name]
         
        for c in ["scale_min","scale_max","scale_steps","scale_type","scale_uni","rotation_min","rotation_max","rotation_steps",\
                  "translation_min","translation_max","translation_steps",\
                  "rotation_neighbor","rotation_grid"]:
            obj["wfc_" +c] = PROP_DEFAULTS[c]
            props[c] = PROP_DEFAULTS[c]
         
        self.report({'INFO'}, f"Transformation constraints of object {obj_name} have been reset.")  

        return {'FINISHED'}
class COLLECTION_OT_WFC3DSelectDropdownObject(bpy.types.Operator):
    """Select object"""
    bl_idname = "collection.wfc_select_dropdown_object"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        collection = props.collection_obj
        obj_name = props.edit_object

        if not collection or obj_name == "NONE":
            self.report({'WARNING'}, "Empty Collection")
            return {'CANCELLED'}

        if obj_name in collection.children and len(collection.children[obj_name].objects)>0:
            obj = collection.children[obj_name].objects[0]
        else:
            obj = collection.objects[obj_name]
        
        if not obj:
            self.report({'WARNING'}, "Object not found")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
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
    """Select object"""
    bl_idname = "collection.wfc_select_neighbor_object"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        obj_name = props.select_neighbor
        collection = props.collection_obj
        if obj_name in collection.children and len(collection.children[obj_name].objects)>0:
            obj = collection.children[obj_name].objects[0]
        else:
            obj = collection.objects[obj_name]
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = obj
        obj.select_set(True)
        return {'FINISHED'}


class COLLECTION_OT_WFC3DGetSelectedObject(bpy.types.Operator):
    """Get active object"""
    bl_idname = "collection.wfc_get_selected_object"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        if context.view_layer.objects.active:
            active_object_name = context.view_layer.objects.active.name
            if active_object_name in props.collection_obj.objects or active_object_name in props.collection_obj.children:
                props.edit_object = active_object_name
        else:
            self.report({'WARNING'}, "No active object found")
            return {'CANCELLED'}
        return {'FINISHED'}

class COLLECTION_OT_WFC3DGetNeighborSelectedObject(bpy.types.Operator):
    """Get active object"""
    bl_idname = "collection.wfc_get_neighbor_selected_object"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        collection = props.collection_obj
        if context.view_layer.objects.active:
            active_object_name = context.view_layer.objects.active.name
            if active_object_name in collection.objects or active_object_name in collection.children:
                props.select_neighbor = active_object_name
            else:
                self.report({'WARNING'}," No active object found")
                return {'CANCELLED'}
        return {'FINISHED'}

operators = [
    COLLECTION_OT_WFC3DAdd_Neighbor_Constraint,
    COLLECTION_OT_WFC3DRemove_Neighbor_Constraint,
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
]
