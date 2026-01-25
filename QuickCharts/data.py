import csv
import re

def get_cell_type(cell):
    if re.match("^[+-]?\d+$", cell):
        cell_type = "int"
    elif re.match("^[0-9.,+-]+$", cell):
        cell_type = "float"
    elif re.match("^\w+$", cell):
        cell_type = "label"
    else:
        cell_type = "label"
    return cell_type

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
                if row_idx == 0 and props.csv_format in {'header','header-left' }: continue
                for col_idx in range(len(row)): # min/max
                    if col_idx >= len(col_sums):
                        col_sums.append(0)
                        abs_col_sums.append(0)
                    if col_idx == 0 and props.csv_format in {'left','header-left' }: continue
                    v = float(row[col_idx])
                    row_sums[row_idx] += v
                    abs_row_sums[row_idx] += abs(v)
                    col_sums[col_idx] += v
                    abs_col_sums[col_idx] += abs(v)
                    minv = min(minv, v) if minv is not None else v
                    maxv = max(maxv, v) if maxv is not None else v
    except Exception as e:
        print(f"Could not read {props.csv_filename}: {e}")
    return  { "rows": rows, "minv": minv, "maxv": maxv,
              "row_sums": row_sums, "abs_row_sums": abs_row_sums,
              "col_sums": col_sums, "abs_col_sums": abs_col_sums }

def update_cell_types(props):
    props.cell_types.clear()
    try:
        header = None
        with open(props.csv_filename, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row_idx, row in enumerate(csv_reader):
                if props.csv_format in {'header','header-left'}:
                    if row_idx == 0 and props.data_series in {'columns'}:
                        header = list(row)
                        continue
                    elif row_idx == 1 and props.data_series in {'columns'}:
                        for cell_idx, cell in enumerate(row):
                            item = props.cell_types.add()
                            item.name = header[cell_idx]
                            item.cell_type = get_cell_type(cell)
                        break
                    else:
                        item = props.cell_types.add()
                        item.name = f"{row[0]}" if props.csv_format in {'header-left'} else f"{row_idx}"
                        item.cell_type = get_cell_type(row[0] if props.csv_format in {'header'} else row[1])
                elif props.csv_format in {'left'}:
                    if props.data_series in {'rows'}:
                        item = props.cell_types.add()
                        item.name = f"{row[0]}"
                        item.cell_type = get_cell_type(row[1])
                    elif props.data_series in {'columns'}:
                        for cell_idx, cell in enumerate(row):
                            item = props.cell_types.add()
                            item.name = f"{cell_idx}"
                            item.cell_type = get_cell_type(cell)
                        break
    except Exception as e:
        print(f"Could not read {props.csv_filename}: {e}")
