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