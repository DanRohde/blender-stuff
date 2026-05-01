import bpy
import time
import gc
import functools
import json
import numpy as np
import re
import random
from .generator import WFC3DGenerator
from .renderer import WFC3DRenderer


def hide_recursive(name, collection):
    for child in collection.children:
        hide_recursive(name, child)
    if collection.name.startswith(name): collection.hide_viewport = True

def hide_old_target_collections(props):
    if props.use_parent_object and props.hide_last_target_collections:
        for obj in bpy.data.objects:
            if not obj.name.startswith(props.target_collection): continue
            for child in obj.children:
                child.hide_set(True)
        return True
    if not props.remove_target_collection and props.hide_last_target_collections:
        hide_recursive(props.target_collection, bpy.context.view_layer.layer_collection)
        return True
    return False

def init_render_result(props):
    props.render_result.cell_count = np.prod(props.grid_size)
    props.render_result.gen_start_time = time.perf_counter()
    props.render_result.empty_cells = -1
    props.render_result.gen_duration = -1
    props.render_result.render_start_time = -1
    props.render_result.render_duration = -1
    props.render_result.object_count = ""
    props.render_result.bb_count = 0
    props.render_result.bb_count_used = 0
    props.render_result.object_total = 0

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

    props.render_result.bb_count = len(generator.objects)
    for v in counts.values():
        props.render_result.bb_count_used += 1 if v > 0 else 0
        props.render_result.object_total += v
    props.render_result.object_count = json.dumps(counts)

def end_render_result(props):
    props.render_result.render_duration = time.perf_counter() - props.render_result.render_start_time

def generate_model(props, context):
    progress_offset = 0
    if props.use_parent_object and props.target_collection in bpy.data.objects and not hide_old_target_collections(props):
        progress_offset = len(bpy.data.objects[props.target_collection].children)
    else:
        if not hide_old_target_collections(props) and props.target_collection in bpy.data.collections:
            progress_offset += len(bpy.data.collections[props.target_collection].objects)
    gs = np.prod(props.grid_size)
    progress = WFC3DProgress(progress_offset + 2*gs, context, cursor = not props.background_generation, end_callback = functools.partial(end_render_result, props))
    progress.begin()
    init_render_result(props)
    generator = WFC3DGenerator(props)
    if props.background_generation:
        generator.init_task()
        props.progress_running = True
        props.progress_paused = False
        bpy.app.timers.register(functools.partial(generate_model_task, props, generator, progress), first_interval=0.1)
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
        if props.progress_paused: return 0.1
        idx = 0
        done = False
        while idx < props.background_iterations:
            idx += 1
            if renderer.render_object(progress): continue
            done = True
            break
        if not done: return 0.01
    renderer.clean()
    props.progress_running = False
    props.progress_paused = False
    progress.end()
    return None

def generate_model_task(props, generator, progress):
    if not props.progress_running: return None
    if props.progress_paused: return 0.1
    idx = 0
    while idx < props.background_iterations:
        idx += 1
        if generator.generate_task(progress): continue
        renderer = WFC3DRenderer(generator, props)
        start_render_result(props, generator)
        renderer.init_target_collection(progress)
        bpy.app.timers.register(functools.partial(render_model_task, props, renderer, progress))
        return None
    return 0.01


def handle_seed_change(_self, context):
    props = context.scene.wfc_props
    if props.cherry_picking_running or not props.auto_generate or props.collection_obj is None: return
    if len(props.collection_obj.objects) == 0 and len(props.collection_obj.children) == 0: return
    generate_model(props, context)

class OBJECT_OT_Generate(bpy.types.Operator):
    """Generates a 3D model with Wave Function Collapse"""
    bl_idname = "object.wfc_generate"
    bl_label = "Generate WFC 3D Model"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        generate_model(props, context)
        if not props.background_generation: self.report({'INFO'}, "The WFC 3D model was successfully generated.")
        return {'FINISHED'}

class OBJECT_OT_ResetRenderResult(bpy.types.Operator):
    """Reset render result"""
    bl_idname = "object.wfc_reset_render_result"
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


class OBJECT_OT_StopButton(bpy.types.Operator):
    bl_idname = "object.wfc_stop_button"
    bl_label = ""
    bl_description = "Stop background process."
    prop_name : bpy.props.StringProperty(default="")
    def execute(self, context):
        setattr(context.scene.wfc_props, self.prop_name, False)
        return {'FINISHED'}

class OBJECT_OT_ToggleButton(bpy.types.Operator):
    bl_idname = "object.wfc_toggle_button"
    bl_label = ""
    bl_description = "Pause Toggle"
    prop_name : bpy.props.StringProperty(default="")
    def execute(self, context):
        setattr(context.scene.wfc_props, self.prop_name, not getattr(context.scene.wfc_props, self.prop_name))
        return {'FINISHED'}

class OBJECT_OT_AutoGenerateToggle(bpy.types.Operator):
    """Automatic Model Generation when Random Seed changes."""
    bl_idname = "object.wfc_auto_generate_toggle"
    bl_label = ""
    def execute(self, context):
        context.scene.wfc_props.auto_generate = not context.scene.wfc_props.auto_generate
        return {'FINISHED'}

class OBJECT_OT_CherryPicking(bpy.types.Operator):
    """Start/Pause cherry picking """
    bl_idname = "object.wfc_cherry_picking"
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

class OBJECT_OT_TargetCollectionIncNumber(bpy.types.Operator):
    bl_idname = "object.wfc_target_collection_inc_number"
    bl_label = ""
    bl_description = "Increment/Decrement Number in Name"
    operator:  bpy.props.StringProperty(default="+")
    def execute(self, context):
        props = context.scene.wfc_props
        match = re.search(r'(\d+)$', props.target_collection)
        summand = 1 if self.operator != "-" else -1
        if match:
            number = match.group(1)
            if self.operator == "-" and int(number) == 0:
                props.target_collection = props.target_collection[:match.start()]
                return {'FINISHED'}
            new_number = str(int(number) + summand).zfill(len(number))
            props.target_collection = props.target_collection[:match.start()] + new_number
        else:
            props.target_collection = props.target_collection + "000"
        return {'FINISHED'}
class OBJECT_OT_RandomSeed(bpy.types.Operator):
    bl_idname = "object.wfc_random_seed"
    bl_label = ""
    bl_description = "Set a random random seed"
    def execute(self, context):
        props = context.scene.wfc_props
        random.seed()
        props.seed = random.randint(-0x7fffffff-1, 0x7fffffff)
        return {'FINISHED'}
class OBJECT_OT_ToggleHideCollection(bpy.types.Operator):
    bl_idname = "object.wfc_toggle_hide_collection"
    bl_label = ""
    bl_description = "Show/Hide Collection"
    target: bpy.props.StringProperty(default="")
    target_type: bpy.props.StringProperty(default="collection")
    attribute_name: bpy.props.StringProperty(default="hide_viewport")
    def execute(self, context):
        if self.target_type == "collection":
            target_obj = context.view_layer.layer_collection.children[self.target] if self.target in context.view_layer.layer_collection.children else None
        else:
            target_obj = context.scene.objects[self.target] if self.target in context.scene.objects else None
        if target_obj is None: return {'CANCELLED'}
        obj_list = [ target_obj ]
        if self.target_type == "object":
            obj_list.extend(target_obj.children)

        for obj in obj_list:
            if self.attribute_name == "hide_render" and self.target_type == "collection":
                obj.collection.hide_render = not obj.collection.hide_render
            elif self.attribute_name == "hide_viewport" and self.target_type == "object":
                obj.hide_set(not obj.hide_get())
            else:
                setattr(obj, self.attribute_name, not getattr(obj, self.attribute_name))

        return {'FINISHED'}

class OBJECT_OT_ToggleRelationshipLines(bpy.types.Operator):
    bl_idname = "object.wfc_toggle_lines"
    bl_label = ""
    bl_description = "Toggle Relationship Lines"
    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.overlay.show_relationship_lines = not space.overlay.show_relationship_lines
        return {"FINISHED"}

operators = [ OBJECT_OT_ToggleRelationshipLines, OBJECT_OT_ToggleHideCollection, OBJECT_OT_RandomSeed, OBJECT_OT_TargetCollectionIncNumber,
              OBJECT_OT_ResetRenderResult, OBJECT_OT_AutoGenerateToggle, OBJECT_OT_CherryPicking, OBJECT_OT_ToggleButton, OBJECT_OT_StopButton,
              OBJECT_OT_Generate ]