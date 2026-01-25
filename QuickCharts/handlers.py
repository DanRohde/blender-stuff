import csv
import re
from .data import get_cell_type, update_cell_types

def handle_csv_filename_update(self, _context):

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

    elif re.match("^[0-9.+-]+", rows[1][0]):
        self.csv_format = 'header'
        self.data_series = 'columns'
        self.legend = True
    else:
        self.csv_format = 'header-left'
        self.data_series = 'columns'
        self.legend = False

    return None

def handle_data_series_update(self, _context):
    update_cell_types(self)