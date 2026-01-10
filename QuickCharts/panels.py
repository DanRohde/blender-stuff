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
    row.prop(props, "roughness", text="")
    row.prop(props, "metallic", text="")
    row.prop(props, "alpha", text="")

    row = layout.row(align=True)
    row.prop(props, "label_roughness", text="")
    row.prop(props, "label_metallic", text="")
    row.prop(props, "label_color", text="")

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
        for k in props.keys():
            if hasattr(op, k): setattr(op, k, getattr(props,k))
        
        return None


panels = [ VIEW3D_UL_ColumnTypesList, VIEW3D_PT_Panel ]