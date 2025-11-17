import bpy

import json
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

class WFC3D_OT_ImportJson(bpy.types.Operator, ImportHelper):
    bl_idname = "wfc3d.import_json"
    bl_label = "Import Constraints"
    bl_description = "Import constraints from json file"
    bl_options = {'UNDO'}
    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    def execute(self, context):
        filepath = self.filepath
        try:
            with open(filepath, "r", encoding='utf-8') as fp:
                data = json.load(fp)

            self.report({'INFO'}, "Imported constraints from json file")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, "Import constraints from json file failed")
            return {'CANCELLED'}

class WFC3D_OT_ExportJson(bpy.types.Operator, ExportHelper):
    bl_idname = "wfc3d.export_json"
    bl_label = "Export Constraints"
    bl_description = "Export constraints to json file"
    bl_options = {'UNDO'}
    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    def execute(self, context):
        filepath = self.filepath
        try:
            with open(filepath, "w", encoding='utf-8') as fp:
                json.dump(data, fp, indent=4)
            self.report({'INFO'}, "Exported constraints to json file")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, "Export constraints to json file failed")
            return {'CANCELLED'}

operators = [ WFC3D_OT_ImportJson, WFC3D_OT_ExportJson ]