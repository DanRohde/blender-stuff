import bpy
import time

from .constants import PRIORITY_ICONS
def format_duration(duration):
    days, remainder = divmod(duration, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, remainder = divmod(remainder, 60)
    return f"{days:.0f}d {hours:02.0f}h {minutes:02.0f}m" if days > 0 else f"{hours:02.0f}h {minutes:02.0f}m"

def draw_task_actions(layout, item, task_index, time_tracking = True):
    if time_tracking:
        c = layout.column(align=True)
        c.operator("object.stodo_toggle_running_task", emboss=False, icon="PLAY" if item.start_time == -1 else "EVENT_MEDIASTOP").task_index = task_index
        c.enabled = not item.done
    layout.column(align=True).prop(item, "done", text="")#, icon="STRIP_COLOR_05" if item.done else "STRIP_COLOR_03")

def draw_task_progress(layout, item):
    if item.duration == 0 and item.start_time <= 0: return
    c = layout.column(align=True)
    c.alignment = "LEFT"
    duration = item.duration if item.start_time == -1 else item.duration + time.time() - item.start_time
    if duration < 0: duration = 0
    c.label(text=format_duration(duration))
    if item.time_required_days + item.time_required_hours + item.time_required_minutes > 0:
        tr = item.time_required_days * 86400 + item.time_required_hours * 3600 + item.time_required_minutes * 60
        p = duration / tr
        if tr - duration > 0:
            layout.progress(factor=p, text=f"{p * 100:03.1f}% used, {format_duration(tr - duration)} remaining", type="RING")
        else:
            layout.label(text=f"Time expired {format_duration(abs(tr - duration))} ago.", icon="WARNING_LARGE")

def draw_tasks_progress(layout, props):
    if len(props.task_list) > 0:
        done = len([i for i in props.task_list if i.done])
        progress = done / len(props.task_list) if len(props.task_list) > 0 else 0
        layout.progress(factor=progress, text=f"{progress * 100:03.1f} % ({done} of {len(props.task_list)}) done.")

class STODO_UL_TaskList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        prefs = bpy.context.preferences.addons[__package__].preferences

        col = layout.row().column(align=True)
        row = col.row(align=True)
        row.prop(item, "collapsed", text="", emboss=False, icon="RIGHTARROW" if item.collapsed else "DOWNARROW_HLT")
        row.prop(item, "selected", text="", icon=PRIORITY_ICONS[item.priority])
        row.prop(item, "task", text="", placeholder="Task")
        draw_task_actions(row, item, index, prefs.enable_time_tracking)

        if not item.collapsed or item.duration > 0 or item.start_time > 0 : col = col.box()

        if item.duration > 0 or item.start_time > 0:
            row = col.row(align=True)
            row.column()
            draw_task_progress(row, item)
        if item.collapsed: return
        row = col.row(align=True)
        row.prop(item, "description", placeholder="Short description")
        col.row().prop(item, "priority")

        if prefs.enable_time_tracking:
            row = col.row()
            row.label(text="Planned:")
            row.prop(item, "time_required_days")
            row.prop(item, "time_required_hours")
            row.prop(item, "time_required_minutes")

            row = col.row(align=True)
            c = row.column(align=True)
            c.prop(item, "duration", text="Duration (s):")
            c.enabled = item.start_time == -1
            if item.start_time > 0: col.row().label(text=f"Started on {time.strftime('%x at %X', time.localtime(item.start_time))}")
        if item.created > 0: col.row().label(text=f"Created on {time.strftime('%x at %X', time.localtime(item.created))}")

class STODO_PT_Panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_simple_todo_panel"
    bl_label = "SimpleToDo"
    bl_description = "SimpleToDo Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tasks'
    def draw(self, context):
        layout = self.layout
        props = context.scene.stodo_props
        selected_items = [item for item in props.task_list if item.selected]
        started_items = [item for item in props.task_list if item.start_time > 0]
        layout.row().prop(props, "quick_add_task", placeholder="Add a new task", icon=PRIORITY_ICONS["normal"])
        row = layout.row()
        row.operator("object.stodo_add_task", text="Add Task", icon="ADD")
        c = row.column()
        c.operator("object.stodo_remove_selected_tasks", icon="REMOVE", text="")
        c.enabled = len(selected_items) > 0
        layout.template_list("STODO_UL_TaskList","", props, "task_list", props, "task_list_idx")
        draw_tasks_progress(layout, props)
        row = layout.row()
        row.operator("object.stodo_add_task", text="Add Task", icon="ADD")
        c = row.column()
        c.operator("object.stodo_remove_selected_tasks", icon="REMOVE", text="")
        c.enabled = len(selected_items) > 0
        box = layout.box()
        row = box.row(align=True)
        row.enabled = len(props.task_list) > 0
        c = row.column()
        c.operator("object.stodo_move_up_tasks", icon="TRIA_UP")
        c.enabled = len(selected_items) > 0
        c = row.column()
        c.operator("object.stodo_move_down_tasks", icon="TRIA_DOWN")
        c.enabled = len(selected_items) > 0
        row.separator()
        row.operator("object.stodo_toggle_select_tasks", icon="CHECKBOX_HLT").select = True
        row.operator("object.stodo_toggle_select_tasks", icon="CHECKBOX_DEHLT").select = False
        row.operator("object.stodo_invert_selected_tasks", icon="CHECKMARK")
        row.separator()
        row.operator("object.stodo_collapse_tasks", icon="RIGHTARROW")
        box.row().label(text=f"{len(selected_items)} of {len(props.task_list)} task(s) selected. {len(started_items)} task(s) started.")
        row = box.row()
        row.operator("object.stodo_export_csv")
        row.enabled = len(props.task_list) > 0
        box.row().operator("object.stodo_import_csv")

def draw_top_bar(self, context):
    if context.region.alignment == 'RIGHT': return
    layout = self.layout
    props = context.scene.stodo_props
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.show_quick_add:
        layout.prop(props, "quick_add_task", icon=PRIORITY_ICONS["normal"], placeholder="Add a new task")
    if prefs.show_quick_tasks and len(props.task_list) > 0:
        running_tasks = [ idx for idx, item in enumerate(props.task_list) if item.start_time > -1 ]
        if len(running_tasks) > 0:
            task_index = running_tasks[0]
        else:
            todo_tasks = [idx for idx, item in enumerate(props.task_list) if not item.done]
            if len(todo_tasks) > 0:
                task_index = todo_tasks[0]
            else:
                layout.label(text="All tasks have been done.", icon="INFO_LARGE")
                return
        item = props.task_list[task_index]
        layout.prop(item, "task", placeholder="Task", icon=PRIORITY_ICONS[item.priority])
        draw_task_actions(layout, item, task_index, prefs.enable_time_tracking)
        if prefs.enable_time_tracking: draw_task_progress(layout, item)
    if prefs.show_tasks_progress: draw_tasks_progress(layout, props)

panels = [ STODO_UL_TaskList, STODO_PT_Panel ]