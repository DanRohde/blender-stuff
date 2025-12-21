import bpy
from .edit_panel import draw_list_selection_actions, draw_list_order_actions
from .helper import count_selected_items, seed_in_seeds_list

class WFC3D_UL_SeedsList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        row = layout.row()
        col = row.column()
        row = col.row()
        row.prop(item, "selected", text=f"{index+1}) Seed: {item.seed}", icon="BOOKMARKS",)
        row.prop(item, "note", text="")
        row = col.row()
        row.label(text=f"Source: {item.collection_obj.name}")
        row.label(text=f"Entropy: {item.entropy_type}")
        row = col.row()
        row.column(align=True).label(text=f"Grid Size: ")
        row.column(align=True).label(text=f"{item.grid_size[0]:5d}")
        row.column(align=True).label(text=f"{item.grid_size[1]:5d}")
        row.column(align=True).label(text=f"{item.grid_size[2]:5d}")
        if item.auto_detect_spacing:
            col.row().label(text="Automatic spacing detection", icon="CHECKBOX_HLT")
        else:
            row = col.row(align=True)
            row.column(align=True).label(text=f"Cell Spacing: ")
            row.column(align=True).label(text=f"{item.spacing[0]:3.2f} m")
            row.column(align=True).label(text=f"{item.spacing[1]:3.2f} m")
            row.column(align=True).label(text=f"{item.spacing[2]:3.2f} m")
        row = col.row()
        row.column(align=True).label(text=f"Odd Offest: ")
        row.column(align=True).label(text=f"{item.odd_offset[0]:3.2f} m")
        row.column(align=True).label(text=f"{item.odd_offset[1]:3.2f} m")
        row.column(align=True).label(text=f"{item.odd_offset[2]:3.2f} m")
        row = col.row()
        row.label(text="Use Constraints", icon="CHECKBOX_HLT" if item.use_constraints else "CHECKBOX_DEHLT")
        row.label(text="Random Start Cell", icon="CHECKBOX_HLT" if item.random_start_cell else "CHECKBOX_DEHLT")
        col.row().label(text=f"Timestamp: {item.timestamp}")

class WFC3DSeedsPanel(bpy.types.Panel):
    """User interface for WFC 3D Seeds"""
    bl_label = ""
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
        r = col.row()
        draw_list_order_actions(props, r, "seeds_input_list")
        r.label(text=f"Number of Random Seed Bookmarks: {len(props.seeds_input_list)}")
        col = row.column()
        col.operator("object.wfc_add_seed_list_item", icon="BOOKMARKS", text="", depress=seed_in_seeds_list(props)[0])
        c = col.column()
        c.operator("object.wfc_remove_seed_list_items", icon="REMOVE", text="")
        c.enabled = count_selected_items(props.seeds_input_list) > 0
        col.separator()
        draw_list_selection_actions(props, col, "seeds_input_list")

    def draw_header(self, context):
        self.layout.row().label(text="WFC 3D Random Seeds", icon="BOOKMARKS")

panels = [ WFC3D_UL_SeedsList, WFC3DSeedsPanel ]
