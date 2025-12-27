import bpy
from .helper import render_source_collection
class WFC3D_PT_BackupPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_wfc_3d_backup"
    bl_label = "WFC 3D Backup"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Edit'
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        render_source_collection(context, layout)
        box = layout.box()
        box.label(text="Export constraints")
        box.operator("wfc3d.export_json")
        layout.separator()
        box = layout.box()
        box.label(text="Import constraints")
        row = box.row(align=True)
        col = row.column()
        col.prop(props, "backup_import_overwrite")
        col.enabled = not props.backup_import_replace
        row.prop(props, "backup_import_replace")
        if props.backup_import_replace: box.label(text="All existing constraints will be deleted!", icon="WARNING_LARGE")
        elif props.backup_import_overwrite: box.label(text="Existing constraints will be overwritten!", icon="WARNING_LARGE")

        box.operator("wfc3d.import_json")

        layout.separator()
        box = layout.box()
        box.row().label(text="Reset All WFC3D Generator Constraints")
        row = box.row()
        row.prop(props, "reset_all_confirmation")
        col = row.column()
        col.operator("object.wfc_reset_all_constraints").sure = props.reset_all_confirmation
        col.enabled = props.reset_all_confirmation

panels = [ WFC3D_PT_BackupPanel ]