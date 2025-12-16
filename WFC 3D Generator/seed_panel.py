import bpy
from .edit_panel import draw_list_selection_actions
from .helper import count_selected_items, seed_in_seeds_list

class WFC3D_UL_SeedsList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        row = layout.row()
        row.prop(item, "selected", icon="BOOKMARKS")
        row.prop(item, "seed")
        row.prop(item, "note")

class WFC3DSeedsPanel(bpy.types.Panel):
    """User interface for WFC 3D Seeds"""
    bl_label = "WFC 3D Random Seeds"
    bl_idname = "VIEW3D_PT_wfc_3d_seeds"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Gen'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        layout.prop(props,"collection_obj")

        if props.collection_obj is None: return

        row = layout.row()
        col = row.column()
        col.template_list("WFC3D_UL_SeedsList", "", props, "seeds_input_list", props, "seeds_input_list_idx")

        col = row.column()
        col.operator("object.wfc_add_seed_list_item", icon="BOOKMARKS", text="", depress=seed_in_seeds_list(props, props.seed))
        c = col.column()
        c.operator("object.wfc_remove_seed_list_items", icon="REMOVE", text="")
        c.enabled = count_selected_items(props.seeds_input_list) > 0
        draw_list_selection_actions(props, col, "seeds_input_list")

panels = [ WFC3D_UL_SeedsList, WFC3DSeedsPanel ]
