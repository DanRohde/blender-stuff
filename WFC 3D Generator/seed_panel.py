import bpy
from .edit_panel import draw_list_selection_actions
from .helper import count_selected_items, seed_in_seeds_list

class WFC3D_UL_SeedsList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        row = layout.row()
        row.prop(item, "selected", icon="BOOKMARKS")
        col = row.column()
        row = col.row()
        row.label(text=f"Seed: {item.seed}")
        row.label(text="Random Start Cell" , icon="CHECKBOX_HLT" if item.random_start_cell else "CHECKBOX_DEHLT")
        col.row().prop(item, "note")
        col.row().label(text=f"Grid Size: {item.grid_size[0]} x {item.grid_size[1]} x {item.grid_size[2]}")
        if item.auto_detect_spacing:
            col.row().label(text="Automatic spacing detection", icon="CHECKBOX_HLT")
        else:
            col.row().label(text=f"Cell Spacing: {item.spacing[0]}m x {item.spacing[1]}m x {item.spacing[2]}m")
        col.row().label(text=f"Odd Offest: X:{item.odd_offset[0]}m Y:{item.odd_offset[1]}m  Z:{item.odd_offset[2]}m")
        col.row().label(text=f"Source Collection: {item.collection_obj.name}")
        col.row().label(text="Use Constraints", icon="CHECKBOX_HLT" if item.use_constraints else "CHECKBOX_DEHLT")
        col.row().label(text=f"Timestamp: {item.timestamp}")

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

        row = layout.row()
        col = row.column()
        col.template_list("WFC3D_UL_SeedsList", "", props, "seeds_input_list", props, "seeds_input_list_idx", rows=1, maxrows=2)

        col = row.column()
        col.operator("object.wfc_add_seed_list_item", icon="BOOKMARKS", text="", depress=seed_in_seeds_list(props)[0])
        c = col.column()
        c.operator("object.wfc_remove_seed_list_items", icon="REMOVE", text="")
        c.enabled = count_selected_items(props.seeds_input_list) > 0
        col.separator()
        draw_list_selection_actions(props, col, "seeds_input_list")

panels = [ WFC3D_UL_SeedsList, WFC3DSeedsPanel ]
