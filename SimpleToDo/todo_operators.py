import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
import time
import csv

class STODO_OT_AddTask(bpy.types.Operator):
    bl_idname = "object.stodo_add_task"
    bl_label = "Add Task"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        item = context.scene.stodo_props.task_list.add()
        item.created = time.time()
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
            item.duration += abs(time.time() - item.start_time)
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

class STODO_OT_ImportCSV(bpy.types.Operator, ImportHelper):
    bl_idname = "object.stodo_import_csv"
    bl_label = "Import Tasks"
    bl_description = "Import tasks from a CSV file"
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})
    def execute(self, context):
        props = context.scene.stodo_props
        try:
            with open(self.filepath, "r") as csvfile:
                csvreader = csv.DictReader(csvfile, delimiter=",")
                for row in csvreader:
                    item = props.task_list.add()
                    for key, value in row.items():
                        if not hasattr(item, key): continue
                        prop = item.bl_rna.properties[key]
                        if prop.type == "FLOAT":
                            value = float(value)
                        elif prop.type == "INT":
                            value = int(value)
                        elif prop.type == "BOOLEAN":
                            value = value.lower() in {"1", "true", "yes"}
                        setattr(item, key, value)
        except Exception as e:
            self.report({'ERROR'}, f"Importing tasks from CSV file {self.filepath} failed: {e}")
            return {"CANCELLED"}
        self.report({'INFO'}, "Import from CSV complete.")
        return {"FINISHED"}

class STODO_OT_ExportCSV(bpy.types.Operator, ExportHelper):
    bl_idname = "object.stodo_export_csv"
    bl_label = "Export Tasks"
    bl_description = "Export tasks to a CSV"
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})
    def execute(self, context):
        props = context.scene.stodo_props
        if len(props.task_list) == 0:
            self.report({'INFO'}, "No tasks to export")
            return {'FINISHED'}

        try:
            keys =  [p.identifier for p in props.task_list[0].bl_rna.properties if p.identifier not in {"rna_type"}]
            with open(self.filepath, "w", encoding="utf-8") as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_ALL)
                csvwriter.writerow(keys)

                for item in props.task_list:
                    row = [ getattr(item, k) for k in keys ]
                    csvwriter.writerow(row)
        except Exception as e:
            self.report({'ERROR'}, f"Exporting tasks to CSV file {self.filepath} failed: {e}")
            return {'CANCELLED'}
        self.report({'INFO'}, "Export to CSV complete.")
        return {"FINISHED"}

operators = [ STODO_OT_ImportCSV, STODO_OT_ExportCSV, STODO_OT_RemoveSelectedTasks, STODO_OT_InvertSelectTasks, STODO_OT_MoveDownTasks,
              STODO_OT_MoveUpTasks, STODO_OT_ToggleSelectTasks, STODO_OT_ToggleRunningTask, STODO_OT_AddTask ]