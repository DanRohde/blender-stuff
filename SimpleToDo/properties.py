import bpy
import time
from .constants import PRIORITIES, PRIORITY_ICONS

def handle_dummy_update(self, context):
    return None

def handle_done_update(self, context):
    if self.start_time > -1:
        self.duration += abs(time.time() - self.start_time)
        self.start_time = -1
    return None

def handle_quick_add_update(self, context):
    if self.quick_add_task == "": return
    item = self.task_list.add()
    item.created = time.time()
    item.task = self.quick_add_task
    self.quick_add_task = ""

class SimpleToDoTaskItem(bpy.types.PropertyGroup):
    task: bpy.props.StringProperty(name="", description="Task", default="")
    description: bpy.props.StringProperty(name="", description="Description", default="")
    priority: bpy.props.EnumProperty(name="Priority", description="Priority", items=PRIORITIES, default="normal")
    done: bpy.props.BoolProperty(name="", description="Click to change status from 'to do' to 'done' or vice versa.", default=False, update=handle_done_update)
    selected: bpy.props.BoolProperty(name="", description="(De)select task.", default=False)
    start_time: bpy.props.FloatProperty(name="Start Time", default=-1)
    duration: bpy.props.FloatProperty(name="Duration", description="Time used so far", default=0, min=0)
    time_required_days: bpy.props.IntProperty(name="D", description="Planned time required in days", default=0, min=0)
    time_required_hours: bpy.props.IntProperty(name="H", description="Planned time required in hours", default=0, min=0, max=24)
    time_required_minutes: bpy.props.IntProperty(name="M", description="Planned time required in minutes", default=0, min=0, max=60)
    collapsed: bpy.props.BoolProperty(name="", description="(Un)Collapse task details", default=True)
    created: bpy.props.FloatProperty(name="", description="Task creation date", default=0)

class SimpleToDoProperties(bpy.types.PropertyGroup):
    task_list: bpy.props.CollectionProperty(type=SimpleToDoTaskItem)
    task_list_idx: bpy.props.IntProperty()
    refresh_dummy : bpy.props.FloatProperty(update=handle_dummy_update)
    quick_add_task: bpy.props.StringProperty(name="", description="Quickly add a new task.", default="", update=handle_quick_add_update)

class SimpleToDoAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    show_quick_add: bpy.props.BoolProperty(name="Show quick task addition", description="Show quick task addition in the top bar", default=False)
    show_quick_tasks: bpy.props.BoolProperty(name="Show quick task actions", description="Show quick task actions in the top bar", default=True)
    show_tasks_progress: bpy.props.BoolProperty(name="Show tasks progress", description="Show tasks progress in the top bar", default=False)
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_quick_add")
        layout.prop(self, "show_quick_tasks")
        layout.prop(self, "show_tasks_progress")

properties = [ SimpleToDoAddonPreferences, SimpleToDoTaskItem, SimpleToDoProperties ]