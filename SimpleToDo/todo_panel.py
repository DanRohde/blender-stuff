import bpy
import time

from .constants import PRIORITY_ICONS
def format_duration(duration):
    days, remainder = divmod(duration, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, remainder = divmod(remainder, 60)
    return f"{days:.0f}d {hours:02.0f}h {minutes:02.0f}m" if days > 0 else f"{hours:02.0f}h {minutes:02.0f}m"
class STODO_UL_TaskList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        col = layout.row().column(align=True)
        row = col.row(align=True)
        row.prop(item, "collapsed", text="", emboss=False, icon="RIGHTARROW" if item.collapsed else "DOWNARROW_HLT")
        row.prop(item, "selected", text="", icon=PRIORITY_ICONS[item.priority])
        row.prop(item, "task", text="")
        c = row.column(align=True)
        c.operator("object.stodo_toggle_running_task", emboss=False, icon="PLAY" if item.start_time == -1 else "EVENT_MEDIASTOP" ).task_index = index
        c.enabled = not item.done
        c = row.column(align=True)
        c.prop(item, "done", emboss=True, text="", icon="STRIP_COLOR_04" if item.done else "STRIP_COLOR_03")

        if not item.collapsed or item.duration > 0 or item.start_time > 0 : col = col.box()

        c.enabled = item.start_time == -1
        if item.duration > 0 or item.start_time > 0:
            row = col.row(align=True)
            row.column()
            c = row.column(align=True)
            c.alignment = "LEFT"
            duration = item.duration if item.start_time == -1 else item.duration + time.perf_counter()-item.start_time
            c.label(text=format_duration(duration))
            if item.time_required_days + item.time_required_hours + item.time_required_minutes > 0:
                tr = item.time_required_days * 86400 + item.time_required_hours * 3600 + item.time_required_minutes * 60
                p = duration / tr
                if tr-duration > 0:
                    row.progress(factor=p, text=f"{p*100:03.1f}% used, {format_duration(tr-duration)} remaining", type="RING")
                else:
                    row.label(text=f"Time expired {format_duration(abs(tr-duration))} ago.", icon="WARNING_LARGE")
        if item.collapsed: return
        row = col.row(align=True)
        row.prop(item, "description")
        col.row().prop(item, "priority")

        row = col.row()
        row.label(text="Required:")
        row.prop(item, "time_required_days")
        row.prop(item, "time_required_hours")
        row.prop(item, "time_required_minutes")

        row = col.row(align=True)
        c = row.column(align=True)
        c.prop(item, "duration", text="Duration (s):")
        c.enabled = item.start_time == -1


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


        row = layout.row()
        row.operator("object.stodo_add_task", text="Add Task", icon="ADD")
        c = row.column()
        c.operator("object.stodo_remove_selected_tasks", icon="REMOVE", text="")
        c.enabled = len(selected_items) > 0
        layout.template_list("STODO_UL_TaskList","", props, "task_list", props, "task_list_idx", rows=10)
        if len(props.task_list) > 0:
            done = len([i for i in props.task_list if i.done ])
            progress =  done / len(props.task_list) if len(props.task_list) > 0 else 0
            layout.progress(factor = progress, text=f"{progress*100:03.1f} % ({done} of {len(props.task_list)}) done.")
        row = layout.row()
        row.operator("object.stodo_add_task", text="Add Task", icon="ADD")
        c = row.column()
        c.operator("object.stodo_remove_selected_tasks", icon="REMOVE", text="")
        c.enabled = len(selected_items) > 0
        box = layout.box()
        row = box.row()
        row.enabled = len(props.task_list) > 0
        c = row.column()
        c.operator("object.stodo_move_up_tasks", icon="TRIA_UP")
        c.enabled = len(selected_items) > 0
        c = row.column()
        c.operator("object.stodo_move_down_tasks", icon="TRIA_DOWN")
        c.enabled = len(selected_items) > 0
        row.operator("object.stodo_toggle_select_tasks", icon="CHECKBOX_HLT").select = True
        row.operator("object.stodo_toggle_select_tasks", icon="CHECKBOX_DEHLT").select = False
        row.operator("object.stodo_invert_selected_tasks", icon="CHECKMARK")
        box.row().label(text=f"{len(selected_items)} of {len(props.task_list)} task(s) selected.")
panels = [ STODO_UL_TaskList, STODO_PT_Panel ]