# Written 2025 by Dan Rohde
import bpy

from . import properties, operators, panels

classes = (properties.properties + operators.operators + panels.panels)

def add_menu_button(self, context):
    self.layout.operator(operators.OBJECT_OT_CreateChart.bl_idname, text="QuickChart", icon='PLUGIN', )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.quick_charts_props = bpy.props.PointerProperty(type=properties.Properties)
    bpy.types.VIEW3D_MT_add.append(add_menu_button)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_add.remove(add_menu_button)
    del bpy.types.Scene.quick_charts_props


if __name__ == "__main__":
    register()