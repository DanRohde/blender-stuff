import bpy
import time

class WFC3D_OT_RemoveSeedListItems(bpy.types.Operator):
    bl_idname = "object.wfc_remove_seed_list_items"
    bl_label = ""
    bl_description = "Remove selected random seeds from random seeds list."
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
    def execute(self, context):
        props = context.scene.wfc_props
        seeds = [ item.seed for item in props.seeds_input_list ]
        if props.seed in seeds:
            props.seeds_input_list.remove(seeds.index(props.seed))
            return {'FINISHED'}
        item = props.seeds_input_list.add()
        item.seed = props.seed
        item.note = time.strftime("%Y-%m-%d %H:%M:%S")
        return {'FINISHED'}

operators = [ WFC3D_OT_AddSeedListItem, WFC3D_OT_RemoveSeedListItems, ]