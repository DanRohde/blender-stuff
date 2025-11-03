# Written 2025 by Dan Rohde

import bpy

from . import properties, edit_operators, edit_panel, gen_operators, gen_panel, handler, validator_panel, validator_operators


classes = properties.properties + edit_operators.operators + edit_panel.panels + gen_operators.operators + gen_panel.panels + validator_panel.panels + validator_operators.operators

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.wfc_props = bpy.props.PointerProperty(type=properties.WFC3DProperties)
    bpy.app.handlers.depsgraph_update_post.append(handler.update_handler)
    bpy.app.handlers.load_post.append(properties.handle_blend_load)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.depsgraph_update_post.remove(handler.update_handler)
    bpy.app.handlers.load_post.remove(properties.handle_blend_load)
    del bpy.types.Scene.wfc_props

if __name__ == "__main__":
    register()