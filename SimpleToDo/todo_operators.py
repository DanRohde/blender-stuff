import bpy
import time

class STODO_OT_AddTask(bpy.types.Operator):
    bl_idname = "object.stodo_add_task"
    bl_label = "Add Task"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        context.scene.stodo_props.task_list.add()
        return {'FINISHED'}

class STODO_OT_ToggleRunningTask(bpy.types.Operator):
    bl_idname = "object.stodo_toggle_running_task"
    bl_label = ""
    bl_description = "Start/Stop Time Tracking"
    task_index: bpy.props.IntProperty(default=-1)
    def execute(self, context):
        item = context.scene.stodo_props.task_list[self.task_index]
        if item.start_time == -1:
            item.start_time = time.time()
        else:
            item.duration += min(0, time.time() - item.start_time)
            item.start_time = -1
        return {'FINISHED'}

class STODO_OT_ToggleSelectTasks(bpy.types.Operator):
    bl_idname = "object.stodo_toggle_select_tasks"
    bl_label = ""
    bl_description = "(Un)Select all tasks"
    select: bpy.props.BoolProperty(default=True)
    def execute(self, context):
        for item in context.scene.stodo_props.task_list:
            item.selected = self.select
        return {'FINISHED'}

class STODO_OT_InvertSelectTasks(bpy.types.Operator):
    bl_idname = "object.stodo_invert_selected_tasks"
    bl_label = ""
    bl_description = "Invert selection"
    def execute(self, context):
        for item in context.scene.stodo_props.task_list:
            item.selected = not item.selected
        return {'FINISHED'}

class STODO_OT_MoveUpTasks(bpy.types.Operator):
    bl_idname = "object.stodo_move_up_tasks"
    bl_label = ""
    bl_description = "Move selected tasks up"
    def execute(self, context):
        props = context.scene.stodo_props
        selected_indexes = [idx for idx, item in enumerate(props.task_list) if item.selected]
        for idx in selected_indexes:
            if idx > 0: props.task_list.move(idx, idx - 1)
        return {'FINISHED'}

class STODO_OT_MoveDownTasks(bpy.types.Operator):
    bl_idname = "object.stodo_move_down_tasks"
    bl_label = ""
    bl_description = "Move selected tasks down"
    def execute(self, context):
        props = context.scene.stodo_props
        selected_indexes = [idx for idx, item in enumerate(props.task_list) if item.selected]
        for idx in selected_indexes:
            if idx < len(props.task_list) -1 : props.task_list.move(idx, idx + 1)
        return {'FINISHED'}

class STODO_OT_RemoveSelectedTasks(bpy.types.Operator):
    bl_idname = "object.stodo_remove_selected_tasks"
    bl_label = ""
    bl_description = "Remove selected tasks"
    def execute(self, context):
        props = context.scene.stodo_props
        selected_indexes = [idx for idx, item in enumerate(props.task_list) if item.selected]
        for idx in sorted(selected_indexes, reverse=True):
            props.task_list.remove(idx)
        return {'FINISHED'}

operators = [ STODO_OT_RemoveSelectedTasks, STODO_OT_InvertSelectTasks, STODO_OT_MoveDownTasks, STODO_OT_MoveUpTasks, STODO_OT_ToggleSelectTasks, STODO_OT_ToggleRunningTask, STODO_OT_AddTask ]