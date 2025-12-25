import bpy
import numpy as np
import time
from .gen_operators import generate_model, WFC3DProgress, WFC3DGenerator

class WFC3DBackgroundSearch:
    def __init__(self, search_operator = "max", search_scope = "occupancy", search_object = "", search_count = -1):
        self.search_operator = search_operator
        self.search_scope = search_scope
        self.search_object = search_object
        self.search_count = search_count
        self.progress = None
        self.props = None
        self.auto_generate = False
        self.result = None
        self.gs = 0
        self.seed = 0
        self.context = None
        self.generator = None
        self.orig_seed = 0

    def _done(self, props, result = None, seed = None):
        self.progress.end()
        self.progress = None
        self.generator.clean()
        self._set_result(props, self.result if result is None else result, self.seed if seed is None else seed)
        if self.result is None: props.seed = self.orig_seed
        props.auto_generate = self.auto_generate
        props.search_running = False
        if self.result is not None:
            props.seed = self.seed
            if not props.auto_generate: generate_model(props, self.context)
        return None
    def _set_result(self, props, result, seed):
        self.result = result
        self.seed = seed

        props.search_result.result = self.result if self.result is not None else -1
        props.search_result.seed = self.seed
        props.search_result.steps = props.search_iterations - props.search_running_iterations
        props.search_result.duration = time.perf_counter() - props.search_result.start_time

    def _compare_value_with_search_count(self, v):
        if self.search_operator == "<" and v < self.search_count: return True
        elif self.search_operator == "<=" and v <= self.search_count: return True
        elif self.search_operator == "=" and v == self.search_count: return True
        elif self.search_operator == ">=" and v >= self.search_count: return True
        elif self.search_operator == ">" and v > self.search_count: return True
        return False

    def _search(self):
        props = bpy.context.scene.wfc_props
        if props.search_running_iterations == 0 or not props.search_running: return self._done(props)
        if props.search_paused: return 0.01
        self.generator.set_seed(props.seed)
        self.generator.generate_model(self.progress)
        if self.search_scope == "occupancy":
            oc = self.gs - self.generator.grid.count_empty_cells()
        else:
            oc = self.generator.grid.count_obj(self.search_object)
        if (self.search_operator == "max" and (self.result is None or oc > self.result)) or (self.search_operator == "min" and (self.result is None or oc < self.result)):
            self._set_result(props, oc, props.seed)
        if (self.search_operator == "max" and oc == self.gs) or (self.search_operator == "min" and oc == 0): return self._done(props)
        if self._compare_value_with_search_count(oc): return self._done(props, result = oc, seed = props.seed)
        props.seed += 1
        props.search_running_iterations -= 1
        return 0

    def start_search(self, context):
        self.context = context
        props = bpy.context.scene.wfc_props
        props.search_running_iterations = props.search_iterations
        self.auto_generate = props.auto_generate
        props.auto_generate = False
        props.search_result.seed = -1
        props.search_result.result = -1
        props.search_result.steps = -1
        props.search_result.start_time = time.perf_counter()

        props.search_result.search_scope = self.search_scope
        props.search_result.search_object = self.search_object
        props.search_result.search_operator = self.search_operator

        self.orig_seed = props.seed
        self.gs = np.prod(props.grid_size)
        self.progress = WFC3DProgress(props.search_iterations * self.gs, context, prop_prefix="search_", cursor=False)
        self.progress.begin()
        props.search_running = True
        props.search_paused = False
        self.generator = WFC3DGenerator(props)
        bpy.app.timers.register(self._search, first_interval=0)

class WFC3D_OT_Search(bpy.types.Operator):
    """Search for a random seed with maximum grid occupancy"""
    bl_idname = "object.wfc_3d_search"
    bl_label = "Search"
    search_operator : bpy.props.StringProperty(default="min")
    search_scope : bpy.props.StringProperty(default="occupancy")
    search_object : bpy.props.StringProperty(default="")
    search_count : bpy.props.IntProperty(default=-1)
    def execute(self, context):
        search = WFC3DBackgroundSearch(search_operator = self.search_operator, search_scope = self.search_scope, search_object = self.search_object, search_count = self.search_count)
        search.start_search(context)
        return {'FINISHED'}

class WFC3D_OT_ResetSearchResult(bpy.types.Operator):
    """Reset search result"""
    bl_idname = "object.wfc_3d_reset_search_result"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        props.search_result.seed = -1
        props.search_result.empty_cells = -1
        props.search_result.steps = -1
        props.search_result.result = -1
        return {'FINISHED'}


operators = [ WFC3D_OT_Search, WFC3D_OT_ResetSearchResult ]