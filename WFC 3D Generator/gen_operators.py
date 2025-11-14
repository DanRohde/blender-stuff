import bpy

from .generator import WFC3DGenerator

def generate_model(props):
    if not props.remove_target_collection:
        vl = bpy.context.view_layer
        for c in vl.layer_collection.children:
            if c.name.startswith(props.target_collection): c.hide_viewport = True
    generator = WFC3DGenerator(props.collection_obj, props)
    generator.generate_model()
    if props.render_delay == 0: generator.clean()
    return generator

def handle_seed_change(_self, context):
    props = context.scene.wfc_props
    if props.cherry_picking_running or not props.auto_generate or props.collection_obj is None: return
    if len(props.collection_obj.objects) == 0 and len(props.collection_obj.children) == 0: return
    generate_model(props)

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

class OBJECT_OT_WFC3DSearch(bpy.types.Operator):
    """Search for a random seed with maximum grid occupancy"""
    bl_idname = "object.wfc_3d_search"
    bl_label = "Search"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        if props.search_iterations <= 0 or props.collection_obj is None: return {'FINISHED'}
        if len(props.collection_obj.objects) == 0 and len(props.collection_obj.children) == 0: return {'FINISHED'}
        generator = WFC3DGenerator(props.collection_obj, props)
        props.search_result = (-1, -1, -1)
        a = props.auto_generate
        props.auto_generate = False
        i=0
        mincount = 2**63 - 1
        minseed = props.seed
        context.window_manager.progress_begin(0, 100)
        while i < props.search_iterations:
            generator.set_seed(props.seed)
            generator.generate_model(False)
            c = generator.grid.count_empty_cells()
            if c < mincount:
                minseed = props.seed
                mincount = c
            if mincount == 0: break
            props.seed += 1
            i += 1
            context.window_manager.progress_update(100*i/props.search_iterations)

        context.window_manager.progress_end()
        generator.clean()
        props.auto_generate = a
        props.seed = minseed
        props.search_result = (minseed, i, mincount )

        if not props.auto_generate: generate_model(props)
        if mincount == 0:
            self.report({'INFO'}, f"Found a result with full grid occupancy after {i} iteration(s)!")
        else:
            self.report({'INFO'}, f"Found a result with maximum grid occupancy after {i} iteration(s)!")
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

class OBJECT_OT_WFC3DAutoGenerateToggle(bpy.types.Operator):
    """Automatic Model Generation when Random Seed changes."""
    bl_idname = "object.wfc_3d_auto_generate_toggle"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        props.auto_generate = not props.auto_generate
        return {'FINISHED'}

class OBJECT_OT_WFC3DCherryPicking(bpy.types.Operator):
    """Start/Pause cherry picking """
    bl_idname = "object.wfc_3d_cherry_picking"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def _cherry_picking(self):
        props = bpy.context.scene.wfc_props
        prefs = bpy.context.preferences.addons[__package__].preferences
        if not props.cherry_picking_running: return None
        if props.running_delayed_renderer: return prefs.cherry_picking_delay
        props.seed += 1
        generate_model(props)
        return prefs.cherry_picking_delay

    def execute(self, context):
        props = context.scene.wfc_props
        prefs = bpy.context.preferences.addons[__package__].preferences
        if props.collection_obj is None or (len(props.collection_obj.children) == 0 and len(props.collection_obj.objects) == 0): return {'FINISHED'}
        if not props.cherry_picking_running:
            props.cherry_picking_running = True
            props.seed -= 1
            self._cherry_picking()
            bpy.app.timers.register(self._cherry_picking, first_interval=prefs.cherry_picking_delay)
        else:
            props.cherry_picking_running = False
        return {'FINISHED'}


operators = [ OBJECT_OT_WFC3DSearch, OBJECT_OT_WFC3DAutoGenerateToggle, OBJECT_OT_WFC3DCherryPicking, OBJECT_OT_WFC3DGenerateTogglePauseDelayedRenderer, OBJECT_OT_WFC3DGenerateStopDelayedRenderer, OBJECT_OT_WFC3DGenerate ]