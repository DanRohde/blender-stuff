import bpy
import time
import numpy as np
import gc
import functools
from .generator import WFC3DGenerator
from .renderer import WFC3DRenderer


def hide_old_target_collections(props):
    if not props.remove_target_collection:
        vl = bpy.context.view_layer
        for c in vl.layer_collection.children:
            if c.name.startswith(props.target_collection): c.hide_viewport = True
        return True
    return False

def generate_model(props, context):
    progress_offset = 0
    if not hide_old_target_collections(props) and props.target_collection in bpy.data.collections:
        progress_offset += len(bpy.data.collections[props.target_collection].objects)
    gs = props.grid_size[0]*props.grid_size[1]*props.grid_size[2]
    progress = WFC3DProgress(progress_offset + 2*gs, context)
    progress.begin()
    generator = WFC3DGenerator(props)
    if props.background_generation:
        generator.init_task()
        props.progress_running = True
        props.progress_paused = False
        bpy.app.timers.register(functools.partial(generate_model_task, props, generator, progress), first_interval=0)
    else:
        generator.generate_model(progress)
        renderer = WFC3DRenderer(generator, props)
        renderer.render(progress)
        if props.render_delay == 0:
            progress.end()
            renderer.clean()
            gc.collect()
        else:
            progress.set_cursor(False)
    return

def render_model_task(props, renderer, progress):
    if props.progress_running:
        if props.progress_paused: return 0.01
        idx = 0
        done = False
        while idx < props.background_iterations:
            idx += 1
            if renderer.render_object(progress): continue
            done = True
            break
        if not done: return 0
    renderer.clean()
    props.progress_running = False
    props.progress_paused = False
    progress.end()
    return None

def generate_model_task(props, generator, progress):
    if not props.progress_running: return None
    if props.progress_paused: return 0.01
    idx = 0
    while idx < props.background_iterations:
        idx += 1
        if generator.generate_task(progress): continue
        renderer = WFC3DRenderer(generator, props)
        renderer.init_target_collection(progress)
        bpy.app.timers.register(functools.partial(render_model_task, props, renderer, progress))
        return None
    return 0


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

class WFC3DProgress:
    def __init__(self, max_count, context, prop_prefix = '', cursor = True):
        self.max_count = max_count
        self.context = context
        self.start_time = 0
        self.last_count = 0
        self.prop_prefix = prop_prefix
        self.cursor = cursor
    def begin(self):
        if self.cursor: self.context.window_manager.progress_begin(0, 100)
        setattr(self.context.scene.wfc_props, self.prop_prefix+"progress", 0)
        self.start_time = time.perf_counter()
        self.progress_history = []
        self.time_history = []
        self.window_size = 10
    def update(self, count):
        self.last_count = count
        pct = count / self.max_count
        props = self.context.scene.wfc_props
        if self.cursor: self.context.window_manager.progress_update(100 * pct)
        setattr(props, self.prop_prefix+'progress',  pct)
        setattr(props, self.prop_prefix+'progress_elapsed_time', time.perf_counter() - self.start_time)
        self.progress_history.append(pct)
        self.time_history.append(getattr(props,self.prop_prefix+'progress_elapsed_time'))
        setattr(props, self.prop_prefix+'progress_eta', self.get_eta())
    def end(self):
        if self.cursor: self.context.window_manager.progress_end()
        setattr(self.context.scene.wfc_props, self.prop_prefix+'progress', 0)
    def update_inc(self, count = 1):
        self.last_count += count
        self.update(self.last_count)
    def set_cursor(self, cursor):
        if self.cursor and not cursor: self.context.window_manager.progress_end()
        if cursor and not self.cursor: self.context.window_manager.progress_begin()
        self.cursor = cursor
    def get_eta(self):
        if len(self.progress_history) < 2: return -1
        deltas_progress = np.diff(self.progress_history)
        deltas_time = np.diff(self.time_history)
        try:
            speeds = deltas_progress / deltas_time
            window = min(self.window_size, len(speeds))
            smoothed_speed = np.convolve(speeds, np.ones(window) / window, mode='valid')[-1]
            if smoothed_speed <= 0: return -1
            remaining_progress = 1 - self.progress_history[-1]
            eta = remaining_progress / smoothed_speed
        except:
            return -1
        return eta
class WFC3DBackgroundSearch:
    def __init__(self):
        self.progress = None
        self.props = None
        self.auto_generator = False
        self.mincount = 2**63 - 1
        self.minseed = 0
        self.context = None
        self.generator = None
        pass
    def _done(self, props):
        self.progress.end()
        self.progress = None
        self.generator.clean()
        props.search_result = (self.minseed, props.search_iterations - props.search_running_iterations, self.mincount)
        props.auto_generate = self.auto_generate
        props.seed = self.minseed
        props.search_running = False
        if not props.auto_generate: generate_model(props, self.context)

    def _search(self):
        props = bpy.context.scene.wfc_props
        if props.search_running_iterations == 0 or not props.search_running:
            self._done(props)
            return None
        if props.search_paused: return 0.01
        self.generator.set_seed(props.seed)
        self.generator.generate_model(self.progress)
        c = self.generator.grid.count_empty_cells()
        if c < self.mincount:
            self.minseed = props.seed
            self.mincount = c
            props.search_result = (self.minseed, props.search_iterations - props.search_running_iterations, self.mincount)
        if c == 0:
            self._done(props)
            return None
        props.seed += 1
        props.search_running_iterations -= 1
        return 0
    def start_search(self, context):
        self.context = context
        props = bpy.context.scene.wfc_props
        props.search_running_iterations = props.search_iterations
        self.auto_generate = props.auto_generate
        props.auto_generate = False
        props.search_result = (-1, -1, -1)
        self.progress = WFC3DProgress(props.search_iterations * props.grid_size[0] * props.grid_size[1] * props.grid_size[2], context, prop_prefix="search_", cursor=False)
        self.progress.begin()
        props.search_running = True
        self.generator = WFC3DGenerator(props)
        bpy.app.timers.register(self._search, first_interval=0)

class WFC3D_OT_Search(bpy.types.Operator):
    """Search for a random seed with maximum grid occupancy"""
    bl_idname = "object.wfc_3d_search"
    bl_label = "Search"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        search = WFC3DBackgroundSearch()
        search.start_search(context)
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

class WFC3D_OT_StopButton(bpy.types.Operator):
    bl_idname = "object.wfc_3d_stop_button"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    prop_name : bpy.props.StringProperty(default="")
    def execute(self, context):
        setattr(context.scene.wfc_props, self.prop_name, False)
        return {'FINISHED'}

class WFC3D_OT_ToggleButton(bpy.types.Operator):
    bl_idname = "object.wfc_3d_toggle_button"
    bl_label = ""
    prop_name : bpy.props.StringProperty(default="")
    def execute(self, context):
        setattr(context.scene.wfc_props, self.prop_name, not getattr(context.scene.wfc_props, self.prop_name))
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


operators = [ WFC3D_OT_ResetSearchResult, WFC3D_OT_Search, WFC3D_OT_CherryPicking, WFC3D_OT_ToggleButton, WFC3D_OT_StopButton, WFC3D_OT_Generate ]