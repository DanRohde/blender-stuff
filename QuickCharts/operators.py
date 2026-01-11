from bpy.types import Operator
from bpy.props import EnumProperty, FloatVectorProperty, StringProperty, CollectionProperty, IntProperty, BoolProperty, FloatProperty
import csv
import os
from . import render
from .constants import CHART_TYPES, CSV_FORMATS, DATA_SERIES, BC_SUB_TYPES, BC_SHAPES, ROUGHNESS, METALLIC, ALPHA
from .handlers import handle_csv_filename_update
from .properties import CSVColumnTypeItems
from .panels import draw_panel
def read_complete_csv(props):
    rows = []
    row_sums = []
    col_sums = []
    minv = None
    maxv = None
    try:
        with open(props.csv_filename, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row_idx, row in enumerate(csv_reader):
                rows.append(row)
                row_sums.append(0)
                if props.csv_format in {'header','header-left' } and row_idx == 0: continue
                for col_idx in range(len(row)): # min/max
                    if col_idx >= len(col_sums): col_sums.append(0)
                    if props.csv_format in {'left','header-left' } and col_idx == 0: continue
                    v = float(row[col_idx])
                    row_sums[row_idx] += v
                    col_sums[col_idx] += v
                    minv = min(minv, v) if minv is not None else v
                    maxv = max(maxv, v) if maxv is not None else v
    except Exception as e:
        print(f"Could not read {props.csv_filename}: {e}")
    return rows, minv, maxv, row_sums, col_sums
class OBJECT_OT_CreateChart(Operator):
    bl_idname = "object.quick_charts_create_chart"
    bl_label = "Create Chart"
    bl_description = "Create Chart"
    bl_options = {'REGISTER', 'UNDO'}
    csv_filename: StringProperty(name="CSV File", subtype='FILE_PATH', description="CSV File", default="", update=handle_csv_filename_update)
    csv_format: EnumProperty(items=CSV_FORMATS, name="Labels")
    column_types: CollectionProperty(type=CSVColumnTypeItems)
    column_types_idx: IntProperty()

    chart_type: EnumProperty(items=CHART_TYPES, name="Chart Type", description="Chart type", default='column', )
    data_series: EnumProperty(items=DATA_SERIES, name="Data Series", default='columns', )
    bc_shape: EnumProperty(items=BC_SHAPES, name="Shape")
    bc_sub_type: EnumProperty(items=BC_SUB_TYPES, name="Subtype")

    size: FloatVectorProperty(name="Size", description="Chart size", default=(10,10,10), subtype="XYZ_LENGTH")
    spacing: FloatVectorProperty(name="Spacing", description="Chart spacing", default=(0.1,0.1,0.1), subtype="XYZ_LENGTH")

    legend: BoolProperty(name="Legend", default=True)
    labels: BoolProperty(default=True, name="Labels", description="Enable/Disable labels")
    values: BoolProperty(default=True, name="Values", description="Enable/Disable values")

    roughness: FloatProperty(default=ROUGHNESS, name="Roughness", description="Chart Roughness", min=0, max=1)
    metallic: FloatProperty(default=METALLIC, name="Metallic", description="Chart Metallic", min=0, max=1)
    alpha: FloatProperty(default=ALPHA, name="Alpha", description="Chart Alpha", min=0, max=1)

    label_color: FloatVectorProperty(name="Label/Value Color", description="Label/Value color", size=4, subtype="COLOR", default=(1, 1, 1, 1), min=0, max=1)
    label_roughness: FloatProperty(default=ROUGHNESS, name="Label/Value Roughness", description="Label/Value Roughness", min=0, max=1)
    label_metallic: FloatProperty(default=METALLIC, name="Label/Value Metallic", description="Label/Value Metallic", min=0, max=1)

    column_types_collapsed: BoolProperty(default=True, name="Column Types")
    def execute(self, context):
        if self.csv_filename == "": self.csv_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample.csv')
        cvs, minv, maxv, row_sums, col_sums = read_complete_csv(self)
        render.render_chart(self, cvs, minv, maxv, row_sums, col_sums)
        return {'FINISHED'}
    def draw(self, context):
        draw_panel(self, self.layout)
operators= [ OBJECT_OT_CreateChart ]