from bpy.types import Operator

import csv

def read_complete_csv(props):
    chart_properties = props.chart_properties
    csv_properties = props.csv_properties
    chart_properties.min_xyz = (0, 0, 0)
    chart_properties.max_xyz = (10, 10, 10)
    min_x, min_y, min_z = None, None, None
    max_x, max_y, max_z = None, None, None
    rows = []
    try:
        with open(props.csv_filename, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row_idx, row in enumerate(csv_reader):
                rows.append(row)
                if csv_properties.csv_format == 'header' and row_idx == 0: continue
                if csv_properties.csv_format == 'header-left' and row_idx == 0: continue
                for col_idx in range(len(row)): # min/max
                    if csv_properties.csv_format == 'left' and col_idx == 0: continue
                    elif csv_properties.csv_format == 'header-left' and col_idx == 0: continue
                    v = float(row[col_idx])
                    min_z = min(min_z, v) if min_z is not None else v
                    max_z = max(max_z, v) if max_z is not None else v

        if chart_properties.three_d_look:
            min_x, max_x = 0, len(rows) - 1 if chart_properties.data_series == 'columns' else len(rows[0]) - 1
            if chart_properties.bc_sub_type == 'depth':
                min_y, max_y = 0, len(rows[0])-1 if chart_properties.data_series == 'columns' else len(rows)-1
        chart_properties.min_xyz = (min_x if min_x is not None else 0, min_y if min_y is not None else 0, min_z if min_z is not None else 0)
        chart_properties.max_xyz = (max_x if max_x is not None else 0, max_y if max_y is not None else 0, max_z if max_z is not None else 0)
    except Exception as e:
        print(f"Could not read {props.csv_filename}: {e}")
    return rows
class OBJECT_OT_CreateChart(Operator):
    bl_idname = "object.quick_charts_create_chart"
    bl_label = "Create Chart"
    bl_description = "Create Chart"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        read_complete_csv(context.scene.quick_charts_props)
        return {'FINISHED'}
operators= [ OBJECT_OT_CreateChart ]