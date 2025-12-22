import bpy
import time
import gc
import functools
import json
import numpy as np
import re
from .generator import WFC3DGenerator
from .renderer import WFC3DRenderer


def hide_old_target_collections(props):
    if not props.remove_target_collection and props.hide_last_target_collections:
        vl = bpy.context.view_layer
        for c in vl.layer_collection.children:
            if c.name.startswith(props.target_collection): c.hide_viewport = True
        return True
    return False

def init_render_result(props):
    props.render_result.cell_count = props.grid_size[0] * props.grid_size[1] * props.grid_size[2]
    props.render_result.gen_start_time = time.perf_counter()
    props.render_result.empty_cells = -1
    props.render_result.gen_duration = -1
    props.render_result.render_start_time = -1
    props.render_result.render_duration = -1
    props.render_result.object_count = ""

def start_render_result(props, generator):
    props.render_result.gen_duration = time.perf_counter() - props.render_result.gen_start_time
    props.render_result.empty_cells = generator.grid.count_empty_cells()
    props.render_result.render_start_time = time.perf_counter()
    counts = {}
    for o in generator.objects:
        counts[o.name] = 0
    for x in range(generator.grid.grid_size[0]):
        for y in range(generator.grid.grid_size[1]):
            for z in range(generator.grid.grid_size[2]):
                if len(generator.grid.grid[x, y, z]) == 1: counts[generator.grid.grid[x, y, z][0]] += 1
    if props.use_constraints and "dimensions" in generator.constraints.active_constraints:
        for o in generator.objects:
            counts[o.name] = int(counts[o.name] / np.prod(generator.constraints.constraints[o.name]["dim_xyz"]))

    props.render_result.object_count = json.dumps(counts)

def end_render_result(props):
    props.render_result.render_duration = time.perf_counter() - props.render_result.render_start_time

def generate_model(props, context):
    progress_offset = 0
    if not hide_old_target_collections(props) and props.target_collection in bpy.data.collections:
        progress_offset += len(bpy.data.collections[props.target_collection].objects)
    gs = props.grid_size[0]*props.grid_size[1]*props.grid_size[2]
    progress = WFC3DProgress(progress_offset + 2*gs, context, cursor = not props.background_generation, end_callback = functools.partial(end_render_result, props))
    progress.begin()
    init_render_result(props)
    generator = WFC3DGenerator(props)
    if props.background_generation:
        generator.init_task()
        props.progress_running = True
        props.progress_paused = False
        bpy.app.timers.register(functools.partial(generate_model_task, props, generator, progress), first_interval=0)
    else:
        generator.generate_model(progress)
        renderer = WFC3DRenderer(generator, props)
        start_render_result(props, generator)
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
        start_render_result(props, generator)
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

class WFC3D_OT_ResetRenderResult(bpy.types.Operator):
    """Reset render result"""
    bl_idname = "object.wfc_3d_reset_render_result"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        props.render_result.cell_count = -1
        props.render_result.empty_cells = -1
        props.render_result.gen_start_time = -1
        props.render_result.gen_duration = -1
        props.render_result.render_start_time = -1
        props.render_result.render_duration = -1
        props.render_result.object_count = ""
        return {'FINISHED'}

class WFC3DProgress:
    def __init__(self, max_count, context, prop_prefix = '', cursor = True, end_callback = None):
        self.max_count = max_count
        self.context = context
        self.start_time = 0
        self.last_count = 0
        self.prop_prefix = prop_prefix
        self.cursor = cursor
        self.end_callback = end_callback

    def begin(self):
        if self.cursor: self.context.window_manager.progress_begin(0, 100)
        setattr(self.context.scene.wfc_props, self.prop_prefix+"progress", 0)
        self.start_time = time.perf_counter()
    def update(self, count):
        self.last_count = count
        pct = count / self.max_count
        props = self.context.scene.wfc_props
        if self.cursor: self.context.window_manager.progress_update(100 * pct)
        setattr(props, self.prop_prefix+'progress',  pct)
        setattr(props, self.prop_prefix+'progress_elapsed_time', time.perf_counter() - self.start_time)
        setattr(props, self.prop_prefix+'progress_eta', self.get_eta())
    def end(self):
        if self.cursor: self.context.window_manager.progress_end()
        setattr(self.context.scene.wfc_props, self.prop_prefix+'progress', 0)
        if self.end_callback is not None and callable(self.end_callback): self.end_callback()
    def update_inc(self, count = 1):
        self.last_count += count
        self.update(self.last_count)
    def set_cursor(self, cursor):
        if self.cursor and not cursor: self.context.window_manager.progress_end()
        if cursor and not self.cursor: self.context.window_manager.progress_begin()
        self.cursor = cursor
    def get_eta(self):
        if self.last_count <= 0: return 0
        return (self.max_count - self.last_count) * ( time.perf_counter() - self.start_time ) /  self.last_count

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
        props.search_paused = False
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
    bl_description = "Stop background process."
    prop_name : bpy.props.StringProperty(default="")
    def execute(self, context):
        setattr(context.scene.wfc_props, self.prop_name, False)
        return {'FINISHED'}

class WFC3D_OT_ToggleButton(bpy.types.Operator):
    bl_idname = "object.wfc_3d_toggle_button"
    bl_label = ""
    bl_description = "Pause Toggle"
    prop_name : bpy.props.StringProperty(default="")
    def execute(self, context):
        setattr(context.scene.wfc_props, self.prop_name, not getattr(context.scene.wfc_props, self.prop_name))
        return {'FINISHED'}

class WFC3D_OT_AutoGenerateToggle(bpy.types.Operator):
    """Automatic Model Generation when Random Seed changes."""
    bl_idname = "object.wfc_3d_auto_generate_toggle"
    bl_label = ""
    def execute(self, context):
        context.scene.wfc_props.auto_generate = not context.scene.wfc_props.auto_generate
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

class WFC3D_OT_TargetCollectionIncNumber(bpy.types.Operator):
    bl_idname = "object.wfc3d_target_collection_inc_number"
    bl_label = ""
    bl_description = "Increment/Decrement Number in Name"
    operator_name: bpy.props.StringProperty(default="+")
    def execute(self, context):
        props = context.scene.wfc_props
        match = re.search(r'(\d+)$', props.target_collection)
        summand = 1 if self.operator_name != "-" else -1
        if match:
            number = match.group(1)
            if self.operator_name == "-" and int(number) == 0:
                props.target_collection = props.target_collection[:match.start()]
                return {'FINISHED'}
            new_number = str(int(number) + summand).zfill(len(number))
            props.target_collection = props.target_collection[:match.start()] + new_number
        else:
            props.target_collection = props.target_collection + "000"
        return {'FINISHED'}
operators = [ WFC3D_OT_TargetCollectionIncNumber, WFC3D_OT_ResetRenderResult, WFC3D_OT_AutoGenerateToggle, WFC3D_OT_ResetSearchResult, WFC3D_OT_Search, WFC3D_OT_CherryPicking, WFC3D_OT_ToggleButton, WFC3D_OT_StopButton, WFC3D_OT_Generate ]