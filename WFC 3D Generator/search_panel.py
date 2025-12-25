import bpy
from .gen_panel import render_seed_selection, render_generate_button
class WFC3D_PT_SearchPanel(bpy.types.Panel):
    bl_label = "WFC 3D Random Seed Search"
    bl_idname = "VIEW3D_PT_wfc_3d_search"
    bl_description = "WFC 3D Random Seed Search"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Gen'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        prefs = bpy.context.preferences.addons[__package__].preferences

        render_allowed = props.collection_obj is not None and len(props.obj_list) != 0 and props.collection_obj.name != props.target_collection
        layout.label(text="Source Collection")

        layout.prop(props, "collection_obj")
        render_seed_selection(props, prefs, layout.row(align=True), render_allowed)
        render_generate_button(props, layout.row(), render_allowed and not props.search_running)
        box = layout.box()
        box.enabled = render_allowed and not props.cherry_picking_running and props.use_constraints
        box.row().prop(props.search_options, "search_scope")

        row = box.row()
        row.prop(props.search_options, "search_object")
        row.enabled = props.search_options.search_scope == 'number'
        box.row().prop(props.search_options, "search_operator")

        row = box.row()
        row.prop(props.search_options, "search_count", text="Cells" if props.search_options.search_scope == "occupancy" else "Count")
        row.enabled = props.search_options.search_operator not in ["min","max"]
        box.row().prop(props, "search_iterations", text="Iterations", slider=True)

        if props.search_running:
            row = box.row(align=True)
            row.progress(factor=props.search_progress, text=f"{round(props.search_progress * 100)}% (et {round(props.search_progress_elapsed_time, 0):.0f}s/eta {props.search_progress_eta:.0f}s)", type="BAR")
            row.operator("object.wfc_3d_toggle_button", icon="PAUSE", depress=props.search_paused).prop_name = 'search_paused'
            row.operator("object.wfc_3d_stop_button", icon="EVENT_MEDIASTOP").prop_name = 'search_running'
        else:
            row = box.row()
            row.enabled = props.search_options.search_scope == 'occupancy' or props.search_options.search_object is not None
            op = row.operator("object.wfc_3d_search", text="Search Seed")
            op.search_operator, op.search_scope, op.search_object, op.search_count = \
                props.search_options.search_operator, props.search_options.search_scope, \
                    props.search_options.search_object.name if props.search_options.search_object else "", props.search_options.search_count
        if props.search_result.steps > -1:
            box = layout.box()
            row = box.row(align=True)
            row.column().label(text="Search Result")
            row.column().operator("object.wfc_3d_reset_search_result", icon="PANEL_CLOSE")
            if props.search_result.result == -1:
                box.row().label(text=f"Sorry, nothing found.")
            else:
                row = box.row(align=True)
                row.column(align=True).label(text=f"Seed: {props.search_result.seed}")
                row.column(align=True).label(text=f"Step(s): {props.search_result.steps}")
                row = box.row(align=True)

                row.column(align=True).label(text=f"Result: {props.search_result.result} {'Objects' if props.search_result.search_scope == 'number' else 'occupied cells'}")
                row.column(align=True).label(text=f"Duration: {props.search_result.duration:.3f} s")

panels = [ WFC3D_PT_SearchPanel ]