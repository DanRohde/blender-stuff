import bpy

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
            layout.separator()
            layout.prop(props, "rt_rotation_axes")
            if sum(props.rt_rotation_axes) > 0:
                row = layout.row(align=True)
                row.column(align=True).label(text="Angles")
                row.column(align=True).label(text="90°")
                row.column(align=True).label(text="180°")
                row.column(align=True).label(text="270°")
                if props.rt_rotation_axes[0]: layout.prop(props, "rt_rotation_x")
                if props.rt_rotation_axes[1]: layout.prop(props, "rt_rotation_y")
                if props.rt_rotation_axes[2]: layout.prop(props, "rt_rotation_z")
                if sum(props.rt_rotation_axes) > 1: layout.prop(props, "rt_combine")

panels = [ WFC3D_PT_RotationToolPanel ]
