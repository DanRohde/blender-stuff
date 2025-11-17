import bpy

class WFC3D_PT_BackupPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_wfc_3d_backup"
    bl_label = "WFC 3D Backup"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Edit'
    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        layout.prop(props, "collection_obj")

        layout.operator("wfc3d.import_json")
        layout.operator("wfc3d.export_json")


panels = [ WFC3D_PT_BackupPanel ]