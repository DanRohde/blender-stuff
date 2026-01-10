from bpy.types import Operator
from bpy.props import EnumProperty, FloatVectorProperty, StringProperty
import csv

from . import render
from .constants import CHART_TYPES, CSV_FORMATS, DATA_SERIES, BC_SUB_TYPES, BC_SHAPES


def read_complete_csv(props):
    props.min_xyz = (0, 0, 0)
    props.max_xyz = (10, 10, 10)
    min_x, min_y, min_z = None, None, None
    max_x, max_y, max_z = None, None, None
    rows = []
    try:
        with open(props.csv_filename, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row_idx, row in enumerate(csv_reader):
                rows.append(row)
                if props.csv_format == 'header' and row_idx == 0: continue
                if props.csv_format == 'header-left' and row_idx == 0: continue
                for col_idx in range(len(row)): # min/max
                    if props.csv_format == 'left' and col_idx == 0: continue
                    elif props.csv_format == 'header-left' and col_idx == 0: continue
                    v = float(row[col_idx])
                    min_z = min(min_z, v) if min_z is not None else v
                    max_z = max(max_z, v) if max_z is not None else v

        min_x, max_x = 0, len(rows) - 1 if props.data_series == 'columns' else len(rows[0]) - 1
        if props.bc_sub_type == 'depth':
            min_y, max_y = 0, len(rows[0])-1 if props.data_series == 'columns' else len(rows)-1
        props.min_xyz = (min_x if min_x is not None else 0, min_y if min_y is not None else 0, min_z if min_z is not None else 0)
        props.max_xyz = (max_x if max_x is not None else 0, max_y if max_y is not None else 0, max_z if max_z is not None else 0)

    except Exception as e:
        print(f"Could not read {props.csv_filename}: {e}")
    return rows
class OBJECT_OT_CreateChart(Operator):
    bl_idname = "object.quick_charts_create_chart"
    bl_label = "Create Chart"
    bl_description = "Create Chart"
    bl_options = {'REGISTER', 'UNDO'}
    csv_filename: StringProperty(options={'HIDDEN'})
    csv_format: EnumProperty(items=CSV_FORMATS, name="Labels")
    chart_type: EnumProperty(items=CHART_TYPES, name="Chart Type", description="Chart type", default='column', )
    data_series: EnumProperty(items=DATA_SERIES, name="Data Series", default='columns', )
    bc_shape: EnumProperty(items=BC_SHAPES, name="Shape")
    bc_sub_type: EnumProperty(items=BC_SUB_TYPES, name="Subtype")
    size: FloatVectorProperty(name="Chart Size", description="Chart size", default=(10,10,10))
    spacing: FloatVectorProperty(name="Spacing", description="Spacing", default=(0.1,0.1,0.1))
    min_xyz: FloatVectorProperty(name="", description="", default=(0, 0, 0), options={'HIDDEN'}, )
    max_xyz: FloatVectorProperty(name="", description="", default=(0, 0, 0), options={'HIDDEN'}, )
    def execute(self, context):
        render.render_chart(self, read_complete_csv(self))
        return {'FINISHED'}
operators= [ OBJECT_OT_CreateChart ]