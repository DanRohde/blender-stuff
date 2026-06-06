import bpy
from .gen_panel import render_seed_selection, render_generate_button, render_render_result
from .helper import render_source_collection

class WFC3D_PT_SearchPanel(bpy.types.Panel):
    bl_label = "WFC 3D Random Seed Search"
    bl_idname = "VIEW3D_PT_wfc_search"
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

        render_source_collection(context, layout)

        render_seed_selection(props, prefs, layout.row(align=True), render_allowed)
        render_generate_button(props, layout.row(), render_allowed and not props.search_running)
        box = layout.box()
        box.enabled = render_allowed and not props.cherry_picking_running and props.use_constraints
        box.row().prop(props.search_options, "search_scope")

        row = box.row()
        row.prop(props.search_options, "search_object")
        row.enabled = props.search_options.search_scope == 'count'
        box.row().prop(props.search_options, "search_operator")

        row = box.row()
        row.prop(props.search_options, "search_count", text="Cells" if props.search_options.search_scope == "occupancy" else "Count")
        row.enabled = props.search_options.search_operator not in ["min","max"]
        box.row().prop(props, "search_iterations", text="Iterations", slider=True)
        box.row().prop(props, "randomize_seed")

        if props.search_running:
            row = box.row(align=True)
            row.progress(factor=props.search_progress, text=f"{round(props.search_progress * 100)}% (et {round(props.search_progress_elapsed_time, 0):.0f}s/eta {props.search_progress_eta:.0f}s)", type="BAR")
            row.operator("object.wfc_toggle_button", icon="PAUSE", depress=props.search_paused).prop_name = 'search_paused'
            row.operator("object.wfc_stop_button", icon="EVENT_MEDIASTOP").prop_name = 'search_running'
        else:
            row = box.row()
            row.enabled = props.search_options.search_scope == 'occupancy' or props.search_options.search_object is not None
            op = row.operator("object.wfc_search", text="Search Seed")
            op.search_operator, op.search_scope, op.search_object, op.search_count, op.randomize_seed = \
                props.search_options.search_operator, props.search_options.search_scope, \
                    props.search_options.search_object.name if props.search_options.search_object else "", props.search_options.search_count, props.randomize_seed 
        if props.search_result.steps > -1:
            box = layout.box()
            row = box.row(align=True)
            row.column().label(text=f"{'Current' if props.search_running else 'Final'} Search Result for {self.build_search_request_string(props)}")
            row.column().operator("object.wfc_reset_search_result", icon="PANEL_CLOSE")
            if props.search_result.result == -1:
                box.row().label(text=f"Sorry, nothing found.")
            else:
                row = box.row(align=True)
                if props.search_result.search_scope == "occupancy":
                    row.column(align=True).label(text=f"{props.search_result.result} occupied cells")
                else:
                    row.column(align=True).label(text=f"{props.search_result.result} x {props.search_result.search_object}")
                row.column(align=True).label(text=f"for seed {props.search_result.seed}")
                row = box.row(align=True)
                row.column(align=True).label(text=f"Step(s): {props.search_result.steps}")
                row.column(align=True).label(text=f"Duration: {props.search_result.duration:.3f} s")
        render_render_result(props, layout)

    def build_search_request_string(self, props):
        if props.search_result.search_operator in ["min","max"]:
            if props.search_result.search_scope == "occupancy":
                ret = f"{props.search_result.search_operator.title()}(Occupancy)"
            else:
                ret = f"{props.search_result.search_operator.title()}(Count[{props.search_result.search_object}])"
        else:
            if props.search_result.search_scope == "occupancy":
                ret = f"Occupancy {props.search_result.search_operator} {props.search_result.search_count}"
            else:
                ret = f"Count[{props.search_result.search_object}] {props.search_result.search_operator} {props.search_result.search_count}"
        return ret
panels = [ WFC3D_PT_SearchPanel ]