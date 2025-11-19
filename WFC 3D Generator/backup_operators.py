import bpy

import json
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from .helper import get_default_empty_name, get_default_empty_object

def remove_existing_constraints(obj):
    for p in obj.keys():
        if p.startswith("wfc_"):
            del obj[p]

def put_data_into_object(data, p, obj):
    try:
        iter(data)
        if '_object_link_' in data:
            obj[p] = bpy.data.objects[data["_object_link_"]]
        else:
            if len(data) == 1:
                obj[p] = data[0]
            else:
                obj[p] = data
    except Exception:
        obj[p] = data

def import_data(props, data):
    collection = props.collection_obj
    default_obj = get_default_empty_object(collection, True)

    #if props.backup_import_replace: remove_existing_constraints(default_obj)
    for p in data["defaults"]:
        if p in default_obj and not props.backup_import_overwrite: continue
        put_data_into_object(data["defaults"][p], p, default_obj)

    for o in data["objects"]:
        if o in collection.objects:
            obj = collection.objects[o]
        elif o in collection.children:
            obj = get_default_empty_object(collection.children[o], True)
        else:
            continue
        #if props.backup_import_replace: remove_existing_constraints(obj)
        for p in data["objects"][o]:
            if p in obj and not props.backup_import_overwrite: continue
            put_data_into_object(data["objects"][o][p], p, obj)

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

            import_data(context.scene.wfc_props, data)
            self.report({'INFO'}, f"Imported constraints from json file {fp.name}.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Import constraints from json file failed: {e}")
            return {'CANCELLED'}

def get_export_data(props):
    data = {
        'version' : '1.0',
        'creator' : 'WFC 3D Generator extension for Blender',
        'defaults' : {},
        'objects' : {},
    }
    for obj in props.collection_obj.objects:
        prop_data = {}
        for p in obj.keys():
            if p.startswith("wfc_"):
                try:
                    iter(obj[p])
                    if len(obj[p]) == 1:
                        prop_data[p] = obj[p][0]
                    else:
                        prop_data[p] = list(obj[p])
                except Exception:
                    if isinstance(obj[p], bpy.types.Object):
                        prop_data[p] = { '_object_link_' : obj[p].name }
                    else:
                        prop_data[p] = obj[p]
        if obj.name.startswith(get_default_empty_name()):
            data['defaults'] = prop_data
        else:
            data["objects"][obj.name] = prop_data
    return data
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
                json.dump(get_export_data(context.scene.wfc_props), fp, indent=4)
            self.report({'INFO'}, f"Exported constraints to json file {fp.name}.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Export constraints to json file failed: {e}")
            return {'CANCELLED'}

operators = [ WFC3D_OT_ImportJson, WFC3D_OT_ExportJson ]