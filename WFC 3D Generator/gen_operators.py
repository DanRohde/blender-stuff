import bpy

from .generator import WFC3DGenerator

class OBJECT_OT_WFC3DGenerate(bpy.types.Operator):
    """Generates a 3D model with Wave Function Collapse"""
    bl_idname = "object.wfc_3d_generate"
    bl_label = "Generate WFC 3D Model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute_prod(self, context):
        props = context.scene.wfc_props
        
        try:
            collection = props.collection_obj
            if not collection:
                raise ValueError(f"Source collection '{props.collection_obj}' not found!")
                
            generator = WFC3DGenerator(collection, props)
            generator.generate_model()
            
            self.report({'INFO'}, "WFC model successfully generated!")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}",)
            return {'CANCELLED'}
        
    def execute(self, context):
        props = context.scene.wfc_props
        
        collection = props.collection_obj
        if not collection:
            raise ValueError(f"Source collection '{props.collection_obj}' not found!")
            
        generator = WFC3DGenerator(collection, props)
        generator.generate_model()
        
        self.report({'INFO'}, "WFC model successfully generated!")
        return {'FINISHED'}
            
operators = [ OBJECT_OT_WFC3DGenerate ]