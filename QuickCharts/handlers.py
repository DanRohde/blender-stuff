import csv
import re

def get_cell_type(cell):
    if re.match("^[+-]?\d+$", cell):
        column_type = "int"
    elif re.match("^[0-9.,+-]+$", cell):
        column_type = "float"
    elif re.match("^\w+$", cell):
        column_type = "label"
    else:
        column_type = "label"
    return column_type

def handle_csv_filename_update(self, context):
    props = context.scene.quick_charts_props
    props.csv_properties.column_types.clear()

    props.chart_properties.chart_type = 'column'
    props.chart_properties.bc_sub_type = 'normal'

    try:
        with open(self.csv_filename, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            rows = []
            for idx, row in enumerate(csv_reader):
                if idx == 2: break
                rows.append(row)
    except Exception as e:
        print(f"Could not read {self.csv_filename}: {e}")
        return None
    #  CSV formats (1: left, 2: header, 3: header-left):
    #  1) label | value | value | ...
    #     label | value | value | ...
    #  2) label | label | label | ...
    #     value | value | value | ...
    #  3) label | label | label | ...
    #     label | value | value | ...
    # value types:
    #   label, float, int, date
    if re.match("^[0-9.,+-]+", rows[0][1]):
        props.csv_properties.csv_format = 'left'

        for i in range(len(rows[0])):
            item = props.csv_properties.column_types.add()
            item.name = rows[0][0]
            item.column_type = "label" if i == 0 else get_cell_type(rows[0][i])

    elif re.match("^[0-9.+-]+", rows[1][0]):
        props.csv_properties.csv_format = 'header'
        props.chart_properties.data_series = 'rows'
        for i in range(len(rows[0])):
            item = props.csv_properties.column_types.add()
            item.name = rows[0][i]
            item.column_type = get_cell_type(rows[1][i])
    else:
        props.csv_properties.csv_format = 'header-left'
        props.chart_properties.chart_type = 'column'
        props.chart_properties.bc_sub_type = 'deep'
        for i in range(len(rows[0])):
            item = props.csv_properties.column_types.add()
            item.name = rows[0][i]
            item.column_type = "label" if i == 0 else get_cell_type(rows[1][i])
    return None