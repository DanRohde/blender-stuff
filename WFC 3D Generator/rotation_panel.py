import bpy
from .helper import get_icon_name, get_selected_items

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

        if not props.collection_obj: return
        newrow = layout.box().row()
        nc = newrow.column().box()
        nc.operator("rotation.wfc_get_selected_object", icon="SELECT_SET")
        nc.prop(props, "rt_auto_active_object", icon="TRIA_RIGHT")
        nc = newrow.column()
        nc.template_list("WFC3D_UL_RotationPanelMultiSelList", "", props, "rt_list", props, "rt_list_idx")
        nc.enabled = not props.rt_auto_active_object
        nc = newrow.column().box()
        nc.operator("rotation.wfc_select_dropdown_object", icon='RESTRICT_SELECT_OFF')
        nc.operator("rotation.wfc_collection_list_select_all", icon="CHECKBOX_HLT")
        nc.operator("rotation.wfc_collection_list_select_none", icon="CHECKBOX_DEHLT")
        nc.operator("collection.wfc_update_collection_list", icon="FILE_REFRESH")
        nc.enabled = not props.rt_auto_active_object

        selected = get_selected_items(props.rt_list)
        if len(selected) == 0: return


        layout.separator()

        box = layout.box()
        row = box.row(align=True)
        row.column(align=True).label(text="Angles:")
        row.column(align=True).label(text="90°")
        row.column(align=True).label(text="180°")
        row.column(align=True).label(text="270°")
        box.row().prop(props, "rt_rotation_x")
        box.row().prop(props, "rt_rotation_y")
        box.row().prop(props, "rt_rotation_z")


        if sum(props.rt_rotation_x) == 0 and sum(props.rt_rotation_y) == 0 and sum(props.rt_rotation_z) == 0: return

        box = layout.box()
        box.row().label(text="Rotate constraints:")
        row = box.row(align=True)

        row.column(align=True)
        row.column(align=True).prop(props, "rt_neighbor")
        row.column(align=True).prop(props, "rt_connector")
        row.column(align=True).prop(props, "rt_geometry")

        if not props.rt_neighbor and not props.rt_connector and not props.rt_geometry: return

        layout.separator()
        layout.box().row(align=True).prop(props, "rt_offset")
        layout.separator()
        layout.label(text=f"{len(selected)*(sum(props.rt_rotation_x)+sum(props.rt_rotation_y)+sum(props.rt_rotation_z))} copies will be created.", icon="INFO_LARGE")
        layout.row(align=True).operator("rotation.wfc_rotation")


panels = [ WFC3D_UL_RotationPanelMultiSelList, WFC3D_PT_RotationToolPanel ]
