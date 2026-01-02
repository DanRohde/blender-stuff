import bpy
from .helper import render_source_collection
class VIEW3D_PT_ValidatorPanel(bpy.types.Panel):
    """User interface for WFC 3D Add-On"""
    bl_label = "WFC 3D Validator"
    bl_idname = "VIEW3D_PT_wfc_validator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Edit'
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        render_source_collection(context, layout)
        if props.collection_obj:
            layout.operator("object.wfc_validator")
            layout.separator()
            if len(props.validator_output_list) > 0:
                layout.template_list("VIEW3D_UL_ValidatorOutputList","",props,"validator_output_list",props,"validator_output_list_idx", sort_lock = True, item_dyntip_propname="description")
                layout.operator("object.wfc_validator_clear_log")

class VIEW3D_UL_ValidatorOutputList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        icon_map = { 0 : 'INFO_LARGE', 1: 'WARNING_LARGE', 2: 'ERROR'}
        layout.label(text=item.logentry,icon=icon_map[item.severity])

panels = [VIEW3D_UL_ValidatorOutputList, VIEW3D_PT_ValidatorPanel]
