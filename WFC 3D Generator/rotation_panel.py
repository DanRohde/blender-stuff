import bpy
from .helper import get_icon_name

class WFC3D_UL_RotationPanelMultiSelList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        layout.row(align=True).prop(item, "selected", text=item.obj.name, icon=get_icon_name(item))

class WFC3D_PT_RotationToolPanel(bpy.types.Panel):
    """User interface for WFC 3D Add-On"""
    bl_label = "WFC 3D Rotation Tool"
    bl_idname = "VIEW3D_PT_wfc_3d_rotation_tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Edit'
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        layout.prop(props, "collection_obj")
        if props.collection_obj:
            layout.template_list("WFC3D_UL_RotationPanelMultiSelList","", props, "rt_list", props, "rt_list_idx")

            layout.separator()

            row = layout.row(align=True)
            row.column(align=True).label(text="Angles:")
            row.column(align=True).label(text="90°")
            row.column(align=True).label(text="180°")
            row.column(align=True).label(text="270°")
            layout.prop(props, "rt_rotation_x")
            layout.prop(props, "rt_rotation_y")
            layout.prop(props, "rt_rotation_z")

            layout.row().label(text="Rotate constraints:")
            row = layout.row(align=True)

            row.column(align=True)
            row.column(align=True).prop(props, "rt_neighbor")
            row.column(align=True).prop(props, "rt_connector")
            row.column(align=True).prop(props, "rt_geometry")

            layout.separator()
            layout.row(align=True).prop(props, "rt_offset")

panels = [ WFC3D_UL_RotationPanelMultiSelList, WFC3D_PT_RotationToolPanel ]
