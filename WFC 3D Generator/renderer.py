import bpy
import gc
import random
from .helper import get_default_empty_name

class WFC3DRenderer:
    def __init__(self, generator, props):
        self.generator = generator
        self.grid = generator.grid
        self.constraints = generator.constraints
        self.props = props
        self.collapsed_cells = self.generator.collapsed_cells
        self.target_collection_obj = None
        self.odd_offset = self.props.odd_offset
        self.location = self.props.location
        self.link_objects = self.props.link_objects
        self.spacing = self.generator.spacing
        self.progress = None

    def render(self, progress=None):
        self.init_target_collection(progress)
        self.progress = progress
        if self.props.render_delay > 0:
            bpy.context.scene.wfc_props.running_delayed_renderer = True
            bpy.app.timers.register(self.place_delayed_objects, first_interval=self.props.render_delay/1000)
        else:
            while len(self.collapsed_cells)>0:
                self.place_object(self.collapsed_cells.pop(0))
                progress.update_inc()

    def place_delayed_objects(self):
        def _cleanup():
            bpy.context.scene.wfc_props.running_delayed_renderer = False
            bpy.context.scene.wfc_props.paused_delayed_renderer = False
            self.progress.end()
            self.clean()
            gc.collect()
        if not bpy.context.scene.wfc_props.running_delayed_renderer:
            _cleanup()
            return None
        if len(self.collapsed_cells) > 0 and not bpy.context.scene.wfc_props.paused_delayed_renderer:
            self.render_object(self.progress)

        if len(self.collapsed_cells) > 0:
            return self.props.render_delay/1000
        else:
            _cleanup()
        return None

    def init_target_collection(self, progress):
        collection_name = self.props.target_collection
        if self.props.remove_target_collection and collection_name in bpy.data.collections:
            for obj in bpy.data.collections[collection_name].objects:
                bpy.data.objects.remove(obj,do_unlink=True)
                if progress: progress.update_inc()
            bpy.data.collections.remove(bpy.data.collections[collection_name])
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        self.target_collection_obj = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(self.target_collection_obj)

    def render_object(self, progress):
        if len(self.collapsed_cells) == 0: return False
        pos = self.collapsed_cells.pop(0)
        skipped = 0
        while len(self.collapsed_cells) > 0 and len(self.grid.grid[pos[0],pos[1],pos[2]]) == 0:
            pos = self.collapsed_cells.pop(0)
            skipped += 1
        self.place_object(pos)
        progress.update_inc(1+skipped)
        return len(self.collapsed_cells) > 0

    def place_object(self, pos):
        x, y, z = pos
        if len(self.grid.grid[x, y, z]) > 0:
            obj_name = self.grid.grid[x, y, z][0]
        else:
            return

        collection = self.target_collection_obj

        # pick random objects from a collection
        if obj_name in bpy.data.collections:
            if self.constraints:
                original_obj = self.constraints.get_random_object_from_collection(pos, bpy.data.collections[obj_name])
            else:
                c = bpy.data.collections[obj_name]
                original_obj = random.choice([o for o in c.objects if not o.name.startswith(get_default_empty_name())])
        else:
            original_obj = next((obj for obj in self.generator.objects if obj.name == obj_name), None)

        if original_obj:
            if self.link_objects:
                try:
                    new_obj = bpy.data.objects.new(name=original_obj.name, object_data=original_obj.data)
                except:
                    new_obj = original_obj.copy()
                    new_obj.data = original_obj.data.copy()

                if self.props.copy_modifiers:
                    for mod in original_obj.modifiers:
                        new_mod = new_obj.modifiers.new(name=mod.name, type=mod.type)
                        for attr in dir(mod):
                            if attr.startswith("_"):
                                continue
                            try:
                                setattr(new_mod, attr, getattr(mod, attr))
                            except Exception:
                                pass
            else:
                new_obj = original_obj.copy()
                new_obj.data = original_obj.data.copy()

            lx, ly, lz = self.location
            new_location = [lx + x * self.spacing[0] + (self.odd_offset[0] * (y % 2)), ly + y * self.spacing[1] + (self.odd_offset[1] * (x % 2)), lz + z * self.spacing[2] + (self.odd_offset[2] * (x % 2))]

            new_obj.location = tuple(new_location)

            if self.props.use_constraints:
                self.constraints.apply_draw_constraints((x, y, z), self.props.spacing, obj_name, new_obj)

            collection.objects.link(new_obj)
    def clean(self):
        self.generator.clean()
        self.generator = None
        self.constraints = None
        self.grid = None
        self.props = None
        self.spacing = None
        self.odd_offset = None
        self.location = None
        self.target_collection_obj = None
        self.progress = None