import bpy

from .generator import WFC3DGenerator
from .constants import CHERRY_PICKING_DELAY



def generate_model(props):
    generator = WFC3DGenerator(props.collection_obj, props)
    generator.generate_model()

class OBJECT_OT_WFC3DGenerate(bpy.types.Operator):
    """Generates a 3D model with Wave Function Collapse"""
    bl_idname = "object.wfc_3d_generate"
    bl_label = "Generate WFC 3D Model"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        props = context.scene.wfc_props
        generate_model(props)
        self.report({'INFO'}, "WFC 3D model successfully generated!")
        return {'FINISHED'}


class OBJECT_OT_WFC3DGenerateStopDelayedRenderer(bpy.types.Operator):
    """Stops running delayed WFC 3D model renderer"""
    bl_idname = "object.wfc_3d_generate_stop_delayed_renderer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        props.running_delayed_renderer = False
        props.paused_delayed_renderer = False
        return {'FINISHED'}

class OBJECT_OT_WFC3DGenerateTogglePauseDelayedRenderer(bpy.types.Operator):
    """Toggle pause for running delayed WFC 3D model renderer"""
    bl_idname = "object.wfc_3d_generate_toggle_pause_delayed_renderer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        props.paused_delayed_renderer = not props.paused_delayed_renderer
        return {'FINISHED'}

class OBJECT_OT_WFC3DCherryPicking(bpy.types.Operator):
    """Toggle cherry picking """
    bl_idname = "object.wfc_3d_cherry_picking"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def _cherry_picking(self):
        props = bpy.context.scene.wfc_props
        if not props.cherry_picking_running: return None
        if not props.remove_target_collection:
            vl = bpy.context.view_layer
            for c in vl.layer_collection.children:
                if c.name.startswith(props.target_collection): c.hide_viewport = True
        props.seed += 1
        generate_model(props)
        return CHERRY_PICKING_DELAY

    def execute(self, context):
        props = context.scene.wfc_props
        if not props.cherry_picking_running:
            props.cherry_picking_running = True
            props.seed -= 1
            self._cherry_picking()
            bpy.app.timers.register(self._cherry_picking, first_interval=CHERRY_PICKING_DELAY)
        else:
            props.cherry_picking_running = False
        return {'FINISHED'}


operators = [ OBJECT_OT_WFC3DCherryPicking, OBJECT_OT_WFC3DGenerateTogglePauseDelayedRenderer, OBJECT_OT_WFC3DGenerateStopDelayedRenderer, OBJECT_OT_WFC3DGenerate ]