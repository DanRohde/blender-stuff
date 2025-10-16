# Written 2025 by Dan Rohde

import bpy

from . import properties, edit_operators, edit_panel, gen_operators, gen_panel, handler


classes = properties.properties + edit_operators.operators + edit_panel.panels + gen_operators.operators + gen_panel.panels

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.wfc_props = bpy.props.PointerProperty(type=properties.WFC3DProperties)
    bpy.app.handlers.depsgraph_update_post.append(handler.on_object_activated)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.wfc_props
    bpy.app.handlers.depsgraph_update_post.remove(handler.on_object_activated)

if __name__ == "__main__":
    register()