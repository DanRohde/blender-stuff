# Written 2025 by Dan Rohde
import bpy

from . import properties, operators, panels

classes = (properties.properties + operators.operators + panels.panels)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.quick_charts_props = bpy.props.PointerProperty(type=properties.Properties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.quick_charts_props


if __name__ == "__main__":
    register()