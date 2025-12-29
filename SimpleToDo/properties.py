import bpy
from .constants import PRIORITIES
class SimpleToDoTaskItem(bpy.types.PropertyGroup):
    task: bpy.props.StringProperty(name="", description="Task", default="")
    description: bpy.props.StringProperty(name="", description="Description", default="")
    priority: bpy.props.EnumProperty(name="Priority", description="Priority", items=PRIORITIES, default="normal")
    done: bpy.props.BoolProperty(name="", description="Status", default=False)
    selected: bpy.props.BoolProperty(name="", description="select", default=False)
    start_time: bpy.props.FloatProperty(name="Start Time", default=-1)
    duration: bpy.props.FloatProperty(name="Duration", default=0)
    time_required_days: bpy.props.IntProperty(name="D", description="Planned time required in days", default=0, min=0)
    time_required_hours: bpy.props.IntProperty(name="H", description="Planned time required in hours", default=0, min=0, max=24)
    time_required_minutes: bpy.props.IntProperty(name="M", description="Planned time required in minutes", default=0, min=0, max=60)
    collapsed: bpy.props.BoolProperty(name="Collapsed", default=True)

class SimpleToDoProperties(bpy.types.PropertyGroup):
    dummy: bpy.props.StringProperty()
    task_list: bpy.props.CollectionProperty(type=SimpleToDoTaskItem)
    task_list_idx: bpy.props.IntProperty()

properties = [ SimpleToDoTaskItem, SimpleToDoProperties ]