import bpy
from bpy.app.handlers import persistent

def redraw_scene():
    props = bpy.context.scene.stodo_props
    if len(props.task_list) > 0:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    return 60

@persistent
def handle_load_post(fn):
    bpy.app.timers.register(redraw_scene, first_interval=0)
