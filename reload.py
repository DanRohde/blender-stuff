import bpy, importlib
import addon_utils
import sys
# "bl_ext.blender_org.wfc_3d_generator"
for a in addon_utils.modules():
    if a.__name__.count("wfc_3d_generator")>0: 
        bpy.ops.preferences.addon_disable(module=a.__name__)
        for name in list(sys.modules.keys()):
            if name.startswith(a.__name__):
                del sys.modules[name]
        importlib.reload(bpy.utils)
        bpy.ops.preferences.addon_enable(module=a.__name__)
        