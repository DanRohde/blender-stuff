from bpy.types import Operator
import csv
import os
from . import render
from .properties import Properties
from .panels import draw_panel
def read_complete_csv(props):
    rows = []
    row_sums = []
    abs_row_sums = []
    col_sums = []
    abs_col_sums = []
    minv = None
    maxv = None
    try:
        with open(props.csv_filename, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row_idx, row in enumerate(csv_reader):
                rows.append(row)
                row_sums.append(0)
                abs_row_sums.append(0)
                if props.csv_format in {'header','header-left' } and row_idx == 0: continue
                for col_idx in range(len(row)): # min/max
                    if col_idx >= len(col_sums):
                        col_sums.append(0)
                        abs_col_sums.append(0)
                    if props.csv_format in {'left','header-left' } and col_idx == 0: continue
                    v = float(row[col_idx])
                    row_sums[row_idx] += v
                    abs_row_sums[row_idx] += abs(v)
                    col_sums[col_idx] += v
                    abs_col_sums[col_idx] += abs(v)
                    minv = min(minv, v) if minv is not None else v
                    maxv = max(maxv, v) if maxv is not None else v
    except Exception as e:
        print(f"Could not read {props.csv_filename}: {e}")
    return  { "rows": rows, "minv": minv, "maxv": maxv, "row_sums": row_sums, "abs_row_sums": abs_row_sums, "col_sums": col_sums, "abs_col_sums": abs_col_sums }
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