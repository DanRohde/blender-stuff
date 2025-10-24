from typing import Any
import bpy
from .constants import DEFAULT_EMPTY_NAME

def get_default_empty_object(collection: object, create: object = False) -> Any | None:
    if DEFAULT_EMPTY_NAME in collection.objects:
        return collection.objects[DEFAULT_EMPTY_NAME]
    else:
        for o in collection.objects:
            if o.name.startswith(DEFAULT_EMPTY_NAME):
                return o
        if not create: return None
        obj = bpy.data.objects.new(DEFAULT_EMPTY_NAME, None)
        collection.objects.link(obj)
        obj.empty_display_type = 'SPHERE'
        obj.location = (0, 0, 0)
        obj.hide_viewport = True
        obj.hide_render = True
        return obj

def get_object_by_name(props, name):
    collection = props.collection_obj
    if props.edit_type == 'objects':
        if name in collection.objects:
            return collection.objects[name]
        elif name in collection.children:
            return get_default_empty_object(collection.children[name], True)
    elif props.edit_type == 'defaults':
        return get_default_empty_object(collection, True)
    return None