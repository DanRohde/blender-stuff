from bpy.types import Panel, UIList

def draw_panel(props, layout):
    layout.prop(props, "csv_filename")
    layout.prop(props, "csv_format")
    layout.prop(props, "data_series")

    row = layout.row(align=True)
    row.alignment = "LEFT"
    row.prop(props, "column_types_collapsed", emboss=False, icon="RIGHTARROW" if props.column_types_collapsed else "DOWNARROW_HLT")
    if not props.column_types_collapsed:
        layout.template_list("VIEW3D_UL_ColumnTypesList", "", props, "column_types", props, "column_types_idx")
    layout.prop(props, "chart_type")
    if props.chart_type in {"column", "bar"}:
        row = layout.row()
        row.prop(props, "bc_shape", text="")
        row.prop(props, "bc_sub_type", text="")

    row = layout.row()
    row.prop(props, "labels")
    row.prop(props, "values")
    row.prop(props, "legend")

    row = layout.row(align=True)
    row.prop(props, "roughness")
    row.prop(props, "metallic")
    row.prop(props, "alpha")

    row = layout.row(align=True)
    row.column().prop(props, "size")
    row.column().prop(props, "spacing")


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
        draw_panel(props, layout)

        op = layout.operator("object.quick_charts_create_chart")
        op.csv_filename = props.csv_filename
        op.csv_format = props.csv_format
        op.chart_type = props.chart_type
        op.data_series = props.data_series
        op.bc_shape = props.bc_shape
        op.bc_sub_type = props.bc_sub_type
        op.size = props.size
        op.spacing = props.spacing

        op.roughness = props.roughness
        op.metallic = props.metallic

        return None


panels = [ VIEW3D_UL_ColumnTypesList, VIEW3D_PT_Panel ]