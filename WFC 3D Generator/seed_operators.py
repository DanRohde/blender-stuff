import bpy
import time

from .helper import seed_in_seeds_list, set_generator_properties_from_bookmark

class WFC3D_OT_SetSeedDirect(bpy.types.Operator):
    bl_idname = "object.wfc_set_seed_direct"
    bl_label = ""
    bl_description = "Apply random seed"
    item_idx : bpy.props.IntProperty()
    def execute(self, context):
        props = context.scene.wfc_props
        set_generator_properties_from_bookmark(props, props.seeds_input_list[self.item_idx])
        return {'FINISHED'}

class WFC3D_OT_RemoveSeedListItems(bpy.types.Operator):
    bl_idname = "object.wfc_remove_seed_list_items"
    bl_label = ""
    bl_description = "Remove selected random seeds from random seeds list."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        selected_indices = [i for i, item in enumerate(props.seeds_input_list) if item.selected]
        for idx in sorted(selected_indices, reverse=True):
            props.seeds_input_list.remove(idx)
        return {'FINISHED'}

class WFC3D_OT_AddSeedListItem(bpy.types.Operator):
    bl_idname = "object.wfc_add_seed_list_item"
    bl_label = ""
    bl_description = "Add/Remove current random seed to/from random seeds list."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.wfc_props
        seed_is_in_list, seeds =  seed_in_seeds_list(props)
        if seed_is_in_list:
            props.seeds_input_list.remove(seeds[0])
            return {'FINISHED'}
        item = props.seeds_input_list.add()
        item.seed = props.seed
        item.grid_size = list(props.grid_size)
        item.spacing = list(props.spacing)
        item.auto_detect_spacing = props.auto_detect_spacing
        item.odd_offset = list(props.odd_offset)
        item.location = list(props.location)
        item.use_constraints = props.use_constraints
        item.random_start_cell = props.random_start_cell
        item.collection_obj = props.collection_obj
        item.entropy_type = props.entropy_type
        item.note = ""
        item.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        auto_generate = props.auto_generate
        props.auto_generate = False
        props.seeds = f"{len(props.seeds_input_list) - 1}"
        props.auto_generate = auto_generate
        return {'FINISHED'}

operators = [ WFC3D_OT_SetSeedDirect, WFC3D_OT_AddSeedListItem, WFC3D_OT_RemoveSeedListItems, ]