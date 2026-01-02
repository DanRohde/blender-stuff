import bpy

import json
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from .helper import get_default_empty_name, get_default_empty_object

def remove_existing_constraints(obj):
    property_keys = [ k for k in obj.keys() if k.startswith("wfc_") ]
    for k in property_keys: del obj[k]

def put_data_into_object(data, p, obj):
    try:
        if isinstance(data, str):
            obj[p] = data
            return
        iter(data)
        if '_object_link_' in data:
            obj[p] = bpy.data.objects[data["_object_link_"]]
        else:
            obj[p] = data[0] if len(data) == 1 else data
    except Exception:
        obj[p] = data

def import_data(props, data):
    collection = props.collection_obj
    default_obj = get_default_empty_object(collection, True)
    if props.backup_import_replace: remove_existing_constraints(default_obj)
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
        if props.backup_import_replace: remove_existing_constraints(obj)
        for p in data["objects"][o]:
            if p in obj and not props.backup_import_overwrite: continue
            put_data_into_object(data["objects"][o][p], p, obj)

class OBJECT_OT_ImportJson(bpy.types.Operator, ImportHelper):
    bl_idname = "object.wfc_import_json"
    bl_label = "Import Constraints"
    bl_description = "Import constraints from a JSON file"
    bl_options = {'UNDO'}
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})
    def execute(self, context):
        filepath = self.filepath
        try:
            with open(filepath, "r", encoding='utf-8') as fp: data = json.load(fp)

            import_data(context.scene.wfc_props, data)
            self.report({'INFO'}, f"Imported constraints from json file {fp.name}.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Import constraints from json file failed: {e}")
            return {'CANCELLED'}

def get_property_data(obj):
    prop_data = {}
    for p in obj.keys():
        if p.startswith("wfc_"):
            try:
                if isinstance(obj[p], str):
                    prop_data[p] = obj[p]
                    continue
                iter(obj[p])
                prop_data[p] = obj[p][0] if len(obj[p]) == 1 else list(obj[p])
            except Exception:
                prop_data[p] = { '_object_link_' : obj[p].name } if isinstance(obj[p], bpy.types.Object) else obj[p]
    return prop_data

def get_export_data(props):
    data = {
        'version' : '1.0',
        'creator' : 'WFC 3D Generator extension for Blender',
        'website' : 'https://extensions.blender.org/add-ons/wfc-3d-generator/',
        'defaults' : {},
        'objects' : {},
    }
    for obj in props.collection_obj.objects:
        prop_data = get_property_data(obj)
        if obj.name.startswith(get_default_empty_name()):
            data['defaults'] = prop_data
        else:
            data["objects"][obj.name] = prop_data
    for child in props.collection_obj.children:
        for obj in child.objects:
            if not obj.name.startswith(get_default_empty_name()): continue
            data["objects"][child.name] = get_property_data(obj)

    return data
class OBJECT_OT_ExportJson(bpy.types.Operator, ExportHelper):
    bl_idname = "object.wfc_export_json"
    bl_label = "Export Constraints"
    bl_description = "Export constraints to a JSON file"
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})
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

operators = [ OBJECT_OT_ImportJson, OBJECT_OT_ExportJson ]