
from bpy.types import Panel, UIList, Operator

def draw_panel(props, layout):
    layout.prop(props, "csv_filename")

    row = layout.row()
    row.prop(props, "chart_type")
    row.prop(props, "data_series")

    if props.chart_type in {"column", "bar"}:
        row = layout.row()
        row.prop(props, "bc_shape", text="")
        row.prop(props, "bc_sub_type", text="")
    if props.chart_type in {"donut"}:
        row = layout.row()
        row.prop(props, "donut_shape")
    row = layout.row()
    row.prop(props, "labels")
    row.prop(props, "values")
    col = row.column()
    col.prop(props, "legend")
    col.enabled = props.chart_type not in {'table'}
    col = row.column()
    col.prop(props, "axes")
    col.enabled = props.chart_type not in {'donut','table'}

    row = layout.row(align=True)
    row.column().prop(props, "size")
    row.column().prop(props, "spacing")

    row = layout.row(align=True)
    row.alignment = "LEFT"
    row.prop(props, "material_collapsed", emboss=False, icon="RIGHTARROW" if props.material_collapsed else "DOWNARROW_HLT")

    if not props.material_collapsed:
        box = layout.box()
        row = box.row()
        row.label(text="")
        row.label(text="Roughness")
        row.label(text="Metallic")
        row.label(text="Alpha/Color")

        row = box.row(align=True)
        row.label(text="Chart:")
        row.prop(props, "roughness", text="")
        row.prop(props, "metallic", text="")
        row.prop(props, "alpha", text="")

        for s in ('label', 'axes', 'value'):
            row = box.row(align=True)
            row.label(text=f"{s.title()}:")
            row.prop(props, f"{s}_roughness", text="")
            row.prop(props, f"{s}_metallic", text="")
            row.prop(props, f"{s}_color", text="")

    row = layout.row(align=True)
    row.alignment="LEFT"
    row.prop(props, "axes_collapsed", emboss=False, icon="RIGHTARROW" if props.axes_collapsed else "DOWNARROW_HLT")
    if not props.axes_collapsed:
        box = layout.box()
        row = box.row(align=True)
        for s in ('x','y','z','values','labels'):
            row.prop(props, f"axes_{s}")
        box.row().prop(props, "axes_shape")
        box.row().prop(props, "axes_thickness")


    if isinstance(props, Operator):
        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(props, "cell_types_collapsed", emboss=False, icon="RIGHTARROW" if props.cell_types_collapsed else "DOWNARROW_HLT")
        if not props.cell_types_collapsed:
            box = layout.box()
            box.row().prop(props, "csv_format")
            box.template_list("VIEW3D_UL_ColumnTypesList", "", props, "cell_types", props, "cell_types_idx")



class VIEW3D_UL_ColumnTypesList(UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.label(text=f"{index+1}. ")
        row.prop(item, "name")
        row.prop(item, "cell_type")
        col = row.column()
        col.alignment = "LEFT"
        col.prop(item, "precision")
        col.enabled = item.cell_type not in {"label"}

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
            if k in {'cell_types'}: continue
            if hasattr(op, k): setattr(op, k, getattr(props,k))
        
        return None


panels = [ VIEW3D_UL_ColumnTypesList  ]