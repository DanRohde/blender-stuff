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
        self.use_cursor = self.props.use_cursor

    def render(self, progress=None):
        self.init_target_collection(progress)
        self.progress = progress
        if self.props.render_delay > 0:
            bpy.context.scene.wfc_props.running_delayed_renderer = True
            bpy.app.timers.register(self.place_delayed_objects, first_interval=self.props.render_delay/1000)
        else:
            while len(self.collapsed_cells) > 0:
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
        if collection_name == "": collection_name = "Object" if self.props.use_parent_object else "Collection"
        if collection_name == self.props.collection_obj.name and not self.props.use_parent_object: collection_name = "Collection.001"
        if self.props.use_parent_object:
            self.target_collection_obj = bpy.context.scene.collection \
                if self.props.collection_obj == bpy.context.view_layer.active_layer_collection.collection \
                else bpy.context.view_layer.active_layer_collection.collection
            if self.props.remove_target_collection and collection_name in bpy.data.objects:
                self.props.parent_object = bpy.data.objects[collection_name]
                children = [ obj for obj in bpy.data.objects if obj.parent == self.props.parent_object]
                for child in children:
                    bpy.data.objects.remove(child, do_unlink=True)
                    if progress: progress.update_inc()
                bpy.data.objects.remove(self.props.parent_object, do_unlink=True)
                bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

            self.props.parent_object = bpy.data.objects.new(collection_name, None)
            self.target_collection_obj.objects.link(self.props.parent_object)
            if self.props.use_cursor:
                self.props.parent_object.location = bpy.context.scene.cursor.location
                self.props.parent_object.rotation_euler = bpy.context.scene.cursor.rotation_euler
            else:
                self.props.parent_object.location = self.location
                self.props.parent_object.rotation_euler = (0, 0, 0)
        else:
            if self.props.remove_target_collection and collection_name in bpy.data.collections:
                for obj in bpy.data.collections[collection_name].objects:
                    bpy.data.objects.remove(obj,do_unlink=True)
                    if progress: progress.update_inc()
                bpy.data.collections.remove(bpy.data.collections[collection_name])
                bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
            self.target_collection_obj = bpy.data.collections.new(collection_name)
            if self.props.collection_obj == bpy.context.view_layer.active_layer_collection.collection:
                bpy.context.scene.collection.children.link(self.target_collection_obj)
            else:
                bpy.context.view_layer.active_layer_collection.collection.children.link(self.target_collection_obj)

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
        if len(self.grid.grid[x, y, z]) == 0: return
        obj_name = self.grid.grid[x, y, z][0]
        collection = self.target_collection_obj

        # pick random objects from a collection
        if obj_name in bpy.data.collections:
            if self.constraints:
                original_obj = self.constraints.get_random_object_from_collection(pos, bpy.data.collections[obj_name])
            else:
                c = bpy.data.collections[obj_name]
                objects = [o for o in c.objects if not o.name.startswith(get_default_empty_name())]
                original_obj = random.choice(objects) if len(objects) > 0 else None
        else:
            original_obj = next((obj for obj in self.generator.objects if obj.name == obj_name), None)

        if not original_obj: return

        if self.link_objects:
            try:
                new_obj = bpy.data.objects.new(name=original_obj.name, object_data=original_obj.data)

                new_obj.rotation_mode = original_obj.rotation_mode
                new_obj.scale = original_obj.scale.copy()
                new_obj.rotation_euler = original_obj.rotation_euler.copy()
                new_obj.rotation_quaternion = original_obj.rotation_quaternion.copy()
                new_obj.rotation_axis_angle = original_obj.rotation_axis_angle[:]
            except:
                new_obj = original_obj.copy()
                new_obj.data = original_obj.data.copy()

            if self.props.copy_modifiers:
                for mod in original_obj.modifiers:
                    new_mod = new_obj.modifiers.new(name=mod.name, type=mod.type)
                    for attr in dir(mod):
                        if attr.startswith("_"): continue
                        try:
                            setattr(new_mod, attr, getattr(mod, attr))
                        except Exception:
                            pass
        else:
            new_obj = original_obj.copy()
            new_obj.data = original_obj.data.copy()

        if self.props.use_parent_object:
            lx, ly, lz = (0, 0, 0)
        else:
            lx, ly, lz = self.location if not self.use_cursor else bpy.context.scene.cursor.location

        new_obj.location = (lx + x * self.spacing[0] + (self.odd_offset[0] * (y % 2)), ly + y * self.spacing[1] + (self.odd_offset[1] * (x % 2)), lz + z * self.spacing[2] + (self.odd_offset[2] * (x % 2)))

        if self.props.use_constraints: self.constraints.apply_draw_constraints((x, y, z), self.props.spacing, obj_name, new_obj)

        if self.props.use_parent_object: new_obj.parent = self.props.parent_object
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