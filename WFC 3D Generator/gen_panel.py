import bpy
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

        layout.label(text="Source Collection")
        
        layout.prop(props, "collection_obj")
       
        box = layout.box()
       
        box.label(text="Grid Size (width/depth/height)")
        box.row().prop(props, "grid_size")
        row = box.row()
        row.label(text="Grid Cell Space")
        row.prop(props, "auto_detect_spacing")
        row = box.row()
        row.prop(props, "spacing")
        row.enabled = not props.auto_detect_spacing
        box.label(text="Odd Offset")
        box.row().prop(props, "odd_offset")
        
        box.prop(props, "use_constraints")
        
        layout.label(text="Target Collection")
        box = layout.box()
        box.prop(props, "target_collection")
        box.prop(props, "link_objects")
        row=box.row()
        row.prop(props, "copy_modifiers")
        row.enabled = props.link_objects
        box.prop(props, "remove_target_collection")


        box = layout.box()
        row = box.row()
        row.prop(props, "render_delay")
        col = row.column()
        col.operator("object.wfc_3d_generate_toggle_pause_delayed_renderer", icon='PAUSE', depress=props.paused_delayed_renderer)
        col.enabled = props.running_delayed_renderer
        col = row.column()
        col.operator("object.wfc_3d_generate_stop_delayed_renderer", icon='EVENT_MEDIASTOP')
        col.enabled = props.running_delayed_renderer
        if props.render_delay>0:
            row = box.row()
            render_time = props.render_delay/1000 * props.grid_size[0] * props.grid_size[1] * props.grid_size[2]
            row.label(text=f"Min. rendering time: {render_time:.2f} second(s).")

        box = layout.box()
        box.prop(props, "random_start_cell")
        row = box.row()
        if props.search_running:
            row.progress(factor=props.search_progress,text=f"{round(props.search_progress*100)}% (et: {round(props.search_progress_elapsed_time,0):.0f}s/eta: {props.search_progress_eta:.0f}s)", type="BAR")
            row.operator("object.wfc_3d_stop_search", icon="EVENT_MEDIASTOP")
        else:
            row.prop(props, "search_iterations",text="Iterations")
            row.operator("object.wfc_3d_search",text="Search Seed")
            row.enabled = render_allowed and not props.cherry_picking_running
        if props.search_result[0] > -1:
            row = box.row()
            row.label(text=f"Seed {props.search_result[0]} found in {props.search_result[1]} steps with {props.search_result[2]} empty cell(s).")
            row.operator("object.wfc_3d_reset_search_result",icon="PANEL_CLOSE")
        row = box.row()
        row.prop(props, "seed")
        if prefs.cherry_picking_delay > 0:
            col = row.column()
            col.operator("object.wfc_3d_cherry_picking", icon='PLAY' if not props.cherry_picking_running else 'PAUSE', depress=props.cherry_picking_running)
            col.enabled = render_allowed
        col = row.column()
        col.operator("object.wfc_3d_auto_generate_toggle", icon='AUTO', depress = props.auto_generate)
        col.enabled = render_allowed and not props.cherry_picking_running and not props.search_running

        layout.separator(type="LINE", factor=0.2)

        if props.remove_target_collection and props.target_collection != "" and props.target_collection in bpy.data.collections:
            layout.box().label(text="Target collection will be removed!", icon="WARNING_LARGE")
            

        row = layout.row()
        row.enabled = render_allowed and not props.running_delayed_renderer
        row.operator("object.wfc_3d_generate")
        if props.progress > 0: layout.row().progress(factor=props.progress, text=f"{round(props.progress*100)}% (et: {round(props.progress_elapsed_time,0):.0f}s/eta: {props.progress_eta:.0f}s)", type="BAR")
        if props.render_delay > 0:
            row = layout.row()
            row.operator("object.wfc_3d_generate_stop_delayed_renderer", text="Stop Delayed Renderer",icon='EVENT_MEDIASTOP')
            row.enabled = props.running_delayed_renderer

        if props.collection_obj is None:
            layout.label(text="Please select a source collection.", icon="INFO_LARGE")
        if props.collection_obj is not None and props.collection_obj.name == props.target_collection:
            layout.label(text="Source and target collection should not be the same.", icon="WARNING_LARGE")
        if props.collection_obj and len(props.collection_obj.objects)==0 and len(props.collection_obj.children)==0:
            layout.label(text="Please select a non-empty source collection.", icon="INFO_LARGE")
            


panels = [ WFC3DGeneratePanel ]
