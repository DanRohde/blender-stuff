import bpy
from bpy.app.handlers import persistent
import time
def redraw_scene():
    props = bpy.context.scene.stodo_props
    props.refresh_dummy = time.time()
    return 60

@persistent
def handle_load_post(_fn):
    bpy.app.timers.register(redraw_scene, first_interval=0)


def handle_dummy_update(_self, _context):
    return None

def handle_done_update(self, _context):
    if self.start_time > -1:
        self.duration += abs(time.time() - self.start_time)
        self.start_time = -1
    return None

def handle_quick_add_update(self, _context):
    if self.quick_add_task == "": return
    item = self.task_list.add()
    item.created = time.time()
    item.task = self.quick_add_task
    self.quick_add_task = ""

