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

def handle_csv_filename_update(self, _context):
    self.column_types.clear()

    self.chart_type = 'column'
    self.bc_sub_type = 'normal'

    if not self.csv_filename or self.csv_filename == "": return None

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
        self.csv_format = 'left'
        self.data_series = 'rows'
        self.legend = False
        if len(rows[0]) > 2: self.bc_sub_type = 'deep'
        for i in range(len(rows[0])):
            item = self.column_types.add()
            item.name = rows[0][0]
            item.column_type = "label" if i == 0 else get_cell_type(rows[0][i])

    elif re.match("^[0-9.+-]+", rows[1][0]):
        self.csv_format = 'header'
        self.data_series = 'columns'
        self.legend = True
        for i in range(len(rows[0])):
            item = self.column_types.add()
            item.name = rows[0][i]
            item.column_type = get_cell_type(rows[1][i])
    else:
        self.csv_format = 'header-left'
        self.chart_type = 'column'
        self.bc_sub_type = 'deep'
        self.legend = True
        for i in range(len(rows[0])):
            item = self.column_types.add()
            item.name = rows[0][i]
            item.column_type = "label" if i == 0 else get_cell_type(rows[1][i])
    return None