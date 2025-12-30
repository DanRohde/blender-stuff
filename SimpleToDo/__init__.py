# Written 2025 by Dan Rohde
import bpy

from . import handler, properties, todo_operators, todo_panel

classes = ( properties.properties + todo_operators.operators + todo_panel.panels )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.stodo_props = bpy.props.PointerProperty(type=properties.SimpleToDoProperties)
    bpy.app.handlers.load_post.append(handler.handle_load_post)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.load_post.remove(handler.handle_load_post)
    del bpy.types.Scene.stodo_props

if __name__ == "__main__":
    register()