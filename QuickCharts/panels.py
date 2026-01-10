from bpy.types import Panel, UIList

class VIEW3D_UL_ColumnTypesList(UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.label(text=f"{index+1}. ")
        row.prop(item, "name")
        row.prop(item, "column_type")
class VIEW3D_PT_Panel(Panel):
    bl_idname = "VIEW3D_PT_quick_charts_panel"
    bl_label = "Quick Charts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Quick Charts"
    def draw(self, context):
        props = context.scene.quick_charts_props
        layout = self.layout
        layout.prop(props, "csv_filename")
        layout.prop(props.csv_properties, "csv_format")
        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(props, "column_types_collapsed", emboss=False, icon="RIGHTARROW" if props.column_types_collapsed else "DOWNARROW_HLT")
        if not props.column_types_collapsed:
            layout.template_list("VIEW3D_UL_ColumnTypesList","", props.csv_properties, "column_types", props.csv_properties, "column_types_idx")
        layout.prop(props.chart_properties, "chart_type")
        row = layout.row(align=True)
        if props.chart_properties.chart_type in {"column","bar"}: row.prop(props.chart_properties, "bc_shape")
        if props.chart_properties.chart_type in {"column","bar"}: layout.prop(props.chart_properties, "bc_sub_type")

        layout.prop(props.chart_properties, "data_series")
        layout.prop(props.chart_properties.legend_properties, "enabled")

        layout.prop(props.chart_properties, "size")

        op = layout.operator("object.quick_charts_create_chart")
        op.csv_filename = props.csv_filename
        op.csv_format = props.csv_properties.csv_format
        op.chart_type = props.chart_properties.chart_type
        op.data_series = props.chart_properties.data_series
        op.bc_shape = props.chart_properties.bc_shape
        op.bc_sub_type = props.chart_properties.bc_sub_type
        op.size = props.chart_properties.size
        op.spacing = props.chart_properties.spacing

        return None


panels = [ VIEW3D_UL_ColumnTypesList, VIEW3D_PT_Panel ]