import bpy
from bpy.app.handlers import persistent
import time
def redraw_scene():
    props = bpy.context.scene.stodo_props
    props.refresh_dummy = time.time()
    return 60

@persistent
def handle_load_post(fn):
    bpy.app.timers.register(redraw_scene, first_interval=0)
