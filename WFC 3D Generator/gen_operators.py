import bpy
import time
import numpy as np
import gc
from .generator import WFC3DGenerator

def generate_model(props, context):
    if not props.remove_target_collection:
        vl = bpy.context.view_layer
        for c in vl.layer_collection.children:
            if c.name.startswith(props.target_collection): c.hide_viewport = True
    gs = props.grid_size[0]*props.grid_size[1]*props.grid_size[2]
    progress = WFC3DProgress(2 * gs, context)
    progress.begin()
    generator = WFC3DGenerator(props)
    generator.generate_model(progress)
    from .renderer import WFC3DRenderer
    renderer = WFC3DRenderer(generator, props)
    progress.set_offset(gs)
    renderer.render(progress)
    progress.end()
    progress = None
    if props.render_delay == 0:
        renderer.clean()
        renderer = None
        gc.collect()
    return generator

def handle_seed_change(_self, context):
    props = context.scene.wfc_props
    if props.cherry_picking_running or not props.auto_generate or props.collection_obj is None: return
    if len(props.collection_obj.objects) == 0 and len(props.collection_obj.children) == 0: return
    generate_model(props, context)

class WFC3D_OT_Generate(bpy.types.Operator):
    """Generates a 3D model with Wave Function Collapse"""
    bl_idname = "object.wfc_3d_generate"
    bl_label = "Generate WFC 3D Model"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        generate_model(props, context)
        self.report({'INFO'}, "WFC 3D model successfully generated!")
        return {'FINISHED'}

class WFC3DProgress():
    def __init__(self, max_count, context, offset = 0):
        self.max_count = max_count
        self.context = context
        self.offset = offset
        self.start_time = 0
    def begin(self):
        self.context.window_manager.progress_begin(0, 100)
        self.context.scene.wfc_props.progress = 0
        self.start_time = time.perf_counter()
        self.progress_history = []
        self.time_history = []
        self.window_size = 10
    def update(self, count):
        pct = (self.offset + count) / self.max_count
        props = self.context.scene.wfc_props
        self.context.window_manager.progress_update(100 * pct)
        props.progress = pct
        props.progress_elapsed_time = time.perf_counter() - self.start_time
        self.progress_history.append(pct)
        self.time_history.append(props.progress_elapsed_time)
        self.context.scene.wfc_props.progress_eta = self.get_eta()
    def end(self):
        self.context.window_manager.progress_end()
        self.context.scene.wfc_props.progress = 0
    def set_offset(self, offset):
        self.offset = offset
    def get_eta(self):
        if len(self.progress_history) < 2: return -1
        deltas_progress = np.diff(self.progress_history)
        deltas_time = np.diff(self.time_history)
        speeds = deltas_progress / deltas_time
        window = min(self.window_size, len(speeds))
        smoothed_speed = np.convolve(speeds, np.ones(window) / window, mode='valid')[-1]
        if smoothed_speed <= 0: return -1
        remaining_progress = 1 - self.progress_history[-1]
        eta = remaining_progress / smoothed_speed
        return eta

class WFC3D_OT_Search(bpy.types.Operator):
    """Search for a random seed with maximum grid occupancy"""
    bl_idname = "object.wfc_3d_search"
    bl_label = "Search"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        if props.search_iterations <= 0 or props.collection_obj is None: return {'FINISHED'}
        if len(props.collection_obj.objects) == 0 and len(props.collection_obj.children) == 0: return {'FINISHED'}
        generator = WFC3DGenerator(props)
        props.search_result = (-1, -1, -1)
        a = props.auto_generate
        props.auto_generate = False
        i=0
        mincount = 2**63 - 1
        minseed = props.seed
        progress = WFC3DProgress(props.search_iterations, context)
        progress.begin()
        while i < props.search_iterations:
            generator.set_seed(props.seed)
            generator.generate_model()
            c = generator.grid.count_empty_cells()
            if c < mincount:
                minseed = props.seed
                mincount = c
            if mincount == 0: break
            props.seed += 1
            i += 1
            progress.update(i)

        progress.end()
        progress = None
        generator.clean()
        gc.collect()
        props.auto_generate = a
        props.seed = minseed
        props.search_result = (minseed, i, mincount )

        if not props.auto_generate: generate_model(props, context)
        if mincount == 0:
            self.report({'INFO'}, f"Found a result with full grid occupancy after {i} iteration(s)!")
        else:
            self.report({'INFO'}, f"Found a result with maximum grid occupancy after {i} iteration(s)!")
        return {'FINISHED'}
class WFC3D_OT_ResetSearchResult(bpy.types.Operator):
    """Reset search result"""
    bl_idname = "object.wfc_3d_reset_search_result"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        props.search_result = (-1, -1, -1)
        return {'FINISHED'}
class WFC3D_OT_GenerateStopDelayedRenderer(bpy.types.Operator):
    """Stops running delayed WFC 3D model renderer"""
    bl_idname = "object.wfc_3d_generate_stop_delayed_renderer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        props.running_delayed_renderer = False
        props.paused_delayed_renderer = False
        return {'FINISHED'}

class WFC3D_OT_GenerateTogglePauseDelayedRenderer(bpy.types.Operator):
    """Toggle pause for running delayed WFC 3D model renderer"""
    bl_idname = "object.wfc_3d_generate_toggle_pause_delayed_renderer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wfc_props
        props.paused_delayed_renderer = not props.paused_delayed_renderer
        return {'FINISHED'}

class WFC3D_OT_AutoGenerateToggle(bpy.types.Operator):
    """Automatic Model Generation when Random Seed changes."""
    bl_idname = "object.wfc_3d_auto_generate_toggle"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        props.auto_generate = not props.auto_generate
        return {'FINISHED'}

class WFC3D_OT_CherryPicking(bpy.types.Operator):
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
        generate_model(props, bpy.context)
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


operators = [ WFC3D_OT_ResetSearchResult, WFC3D_OT_Search, WFC3D_OT_AutoGenerateToggle, WFC3D_OT_CherryPicking, WFC3D_OT_GenerateTogglePauseDelayedRenderer, WFC3D_OT_GenerateStopDelayedRenderer, WFC3D_OT_Generate ]