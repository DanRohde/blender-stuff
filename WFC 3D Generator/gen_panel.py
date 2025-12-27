import bpy
import json
from .helper import seed_in_seeds_list, render_source_collection, render_collection_actions
class WFC3DGeneratePanel(bpy.types.Panel):
    """User interface for WFC 3D Add-On"""
    bl_label = "WFC 3D Generator"
    bl_idname = "VIEW3D_PT_wfc_3d"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Gen'

    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        prefs = bpy.context.preferences.addons[__package__].preferences

        render_allowed = props.collection_obj is not None and len(props.obj_list) != 0 and props.collection_obj.name != props.target_collection

        render_source_collection(context,layout)
        box = layout.box()
       
        box.label(text="Grid Size (width/depth/height)")
        box.row().prop(props, "grid_size")
        if props.grid_size[0] * props.grid_size[1] * props.grid_size[2] > 3000 or props.background_generation:
            row = box.row()
            row.prop(props, "background_generation")
            row.prop(props, "background_iterations")
        row = box.row()
        col = row.column()
        r = col.row(align=True)
        r.label(text="Space")
        r.prop(props, "auto_detect_spacing", text="", icon="CUBE")
        c = col.column(align=True)
        c.prop(props, "spacing")
        c.enabled = not props.auto_detect_spacing
        col = row.column()
        col.label(text="Odd Offset")
        col.prop(props, "odd_offset")
        col = row.column()
        r = col.row(align=True)
        r.label(text="Location")
        r.prop(props, "use_cursor", text="", icon="CURSOR")
        c = col.column(align=True)
        c.prop(props, "location")
        c.enabled = not props.use_cursor

        row = box.row()
        row.prop(props, "use_constraints")

        layout.label(text="Target Collection")
        box = layout.box()
        row = box.row(align=True)
        row.prop(props, "target_collection")
        row.operator("object.wfc3d_target_collection_inc_number", emboss=False, icon="REMOVE").operator = "-"
        row.operator("object.wfc3d_target_collection_inc_number", emboss=False, icon="ADD").operator = "+"

        render_collection_actions(context, row, props.target_collection if props.target_collection != "" else None)

        row = box.row()
        row.prop(props, "link_objects")
        col = row.column()
        col.prop(props, "copy_modifiers")
        col.enabled = props.link_objects

        row = box.row()
        row.prop(props, "remove_target_collection")
        col = row.column()
        col.prop(props, "hide_last_target_collections")
        col.enabled = not props.remove_target_collection

        box = layout.box()
        row = box.row()
        row.prop(props, "render_delay")
        col = row.column()
        col.operator("object.wfc_3d_toggle_button", icon='PAUSE', depress=props.paused_delayed_renderer).prop_name = 'paused_delayed_renderer'
        col.enabled = props.running_delayed_renderer
        col = row.column()
        col.operator("object.wfc_3d_stop_button", icon='EVENT_MEDIASTOP').prop_name ="running_delayed_renderer"
        col.enabled = props.running_delayed_renderer
        if props.render_delay>0:
            row = box.row()
            render_time = props.render_delay/1000 * props.grid_size[0] * props.grid_size[1] * props.grid_size[2]
            row.label(text=f"Min. rendering time: {render_time:.2f} second(s).")

        box = layout.box()
        row = box.row()
        row.prop(props, "random_start_cell")
        col = row.column()
        col.prop(props, "entropy_type")
        col.enabled = props.use_constraints
        row = box.row()
        if props.search_running:
            row.progress(factor=props.search_progress,text=f"{round(props.search_progress*100)}% (et {round(props.search_progress_elapsed_time,0):.0f}s/eta {props.search_progress_eta:.0f}s)", type="BAR")
            row.operator("object.wfc_3d_toggle_button", icon="PAUSE", depress=props.search_paused).prop_name = 'search_paused'
            row.operator("object.wfc_3d_stop_button", icon="EVENT_MEDIASTOP").prop_name = 'search_running'
        else:
            row.prop(props, "search_iterations",text="Iterations")
            op = row.operator("object.wfc_3d_search",text="Search Seed")
            op.search_operator, op.search_scope, op.search_object = "max", "occupancy", ""
            row.enabled = render_allowed and not props.cherry_picking_running and props.use_constraints
        if props.search_result.steps > -1 and props.search_result.search_scope == "occupancy" and props.search_result.search_operator == "max":
            row = box.row()
            row.label(text=f"Seed {props.search_result.seed} found in {props.search_result.steps} steps with {props.search_result.result} occupied cell(s).")
            row.operator("object.wfc_3d_reset_search_result",icon="PANEL_CLOSE")

        render_seed_selection(props, prefs,box.row(align=True), render_allowed)
        layout.separator(type="LINE", factor=0.2)

        if props.remove_target_collection and props.target_collection != "" and props.target_collection in bpy.data.collections:
            layout.box().label(text="Target collection will be removed!", icon="WARNING_LARGE")
            

        render_generate_button(props, layout.row(), render_allowed)

        render_render_result(props, layout)

        if props.collection_obj is None:
            layout.label(text="Please select a source collection.", icon="INFO_LARGE")
        if props.collection_obj is not None and props.collection_obj.name == props.target_collection:
            layout.label(text="Source and target collection should not be the same.", icon="WARNING_LARGE")
        if props.collection_obj and len(props.collection_obj.objects)==0 and len(props.collection_obj.children)==0:
            layout.label(text="Please select a non-empty source collection.", icon="INFO_LARGE")

def render_render_result(props, layout):
    if props.render_result.cell_count > 0:
        box = layout.box()
        row = box.row()
        result = f"C:{props.render_result.cell_count}"
        result += f" E:{props.render_result.empty_cells}" if props.render_result.empty_cells > -1 else ""
        result += f" T:{props.render_result.gen_duration:.2f}s" if props.render_result.gen_duration > -1 else ""
        result += f"/{props.render_result.render_duration:.2f}s" if props.render_result.render_duration > -1 else ""
        result += f"/{props.render_result.gen_duration + props.render_result.render_duration:.2f}s" if props.render_result.gen_duration > -1 and props.render_result.render_duration > -1 else ""
        row.label(text=result, )
        if props.render_result.render_duration > -1: row.operator("object.wfc_3d_reset_render_result", icon="PANEL_CLOSE")
        if props.render_result.object_count != "":
            gf = box.grid_flow(columns=3)
            oc = json.loads(props.render_result.object_count)
            for o in sorted(oc.items(), key=lambda x: x[0]):
                gf.label(text=f"{o[0]}: {o[1]}")
def render_seed_selection(props, prefs, row, render_allowed):
    if len(props.seeds_input_list) > 0: row.prop(props, "seeds", icon="BOOKMARKS", text="")
    row.prop(props, "seed")
    row.operator("object.wfc_random_seed", icon="DOT", text="")
    col = row.column()
    col.operator("object.wfc_add_seed_list_item", icon="BOOKMARKS", text="", depress=seed_in_seeds_list(props)[0])
    col.enabled = render_allowed and not props.search_running
    row.enabled = not props.search_running
    if prefs.cherry_picking_delay > 0:
        col = row.column()
        col.operator("object.wfc_3d_cherry_picking", icon='PLAY' if not props.cherry_picking_running else 'PAUSE', depress=props.cherry_picking_running)
        col.enabled = render_allowed and not props.search_running
    col = row.column()
    col.operator("object.wfc_3d_auto_generate_toggle", icon='AUTO', depress=props.auto_generate)
    col.enabled = render_allowed and not props.cherry_picking_running and not props.search_running

def render_generate_button(props, row, render_allowed):
    if not props.progress_running and not props.running_delayed_renderer:
        row.enabled = render_allowed and not props.running_delayed_renderer and not props.search_running
        row.operator("object.wfc_3d_generate")
    else:
        row.progress(factor=props.progress, text=f"{round(props.progress * 100)}% (et: {round(props.progress_elapsed_time, 0):.0f}s/eta: {props.progress_eta:.0f}s)", type="BAR")
        if props.progress_running:
            row.operator("object.wfc_3d_toggle_button", icon='PAUSE', depress=props.progress_paused).prop_name = "progress_paused"
            row.operator("object.wfc_3d_stop_button", text="", icon='EVENT_MEDIASTOP').prop_name = "progress_running"
        if props.running_delayed_renderer:
            row.operator("object.wfc_3d_toggle_button", icon='PAUSE', depress=props.paused_delayed_renderer).prop_name = "paused_delayed_renderer"
            row.operator("object.wfc_3d_stop_button", text="", icon='EVENT_MEDIASTOP').prop_name = "running_delayed_renderer"
panels = [ WFC3DGeneratePanel ]
