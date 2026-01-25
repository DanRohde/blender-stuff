from bpy.types import Operator
import os
from . import render
from .properties import Properties
from .panels import draw_panel
from .data import read_complete_csv

class OBJECT_OT_CreateChart(Operator, Properties):
    bl_idname = "object.quick_charts_create_chart"
    bl_label = "Create Chart"
    bl_description = "Create Chart"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if self.csv_filename == "": self.csv_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample.csv')
        render.render_chart(self, read_complete_csv(self))
        return {'FINISHED'}
    def draw(self, context):
        draw_panel(self, self.layout)
operators= [ OBJECT_OT_CreateChart ]