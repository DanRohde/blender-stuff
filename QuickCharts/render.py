from mathutils import Vector

from .common import remap, get_color
from .data import get_cell_type
from .objects import *


def create_line_chart(mat, data, x_space, minv, maxv, minz, maxz, z_offset):
    name = "QuickChartLineChart"
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_depth = .1
    curve_data.bevel_resolution = 4
    curve_data.use_fill_caps = True

    polyline = curve_data.splines.new('POLY')
    point_count = len(data)
    polyline.points.add(point_count-1)

    for i in range(point_count):
        print(f"i={i}, data[i]={data[i]}")
        polyline.points[i].co = (i * x_space, 0, remap(float(data[i]), minv, maxv, minz, maxz)-z_offset, 1)

    return create_object(name, curve_data, mat)



def init_target_collection():
    target_collection = bpy.data.collections.new("QuickChartCollection")
    bpy.context.scene.collection.children.link(target_collection)
    chart = bpy.data.objects.new("QuickChart", None)
    chart.empty_display_type = 'ARROWS'
    chart.location = bpy.context.scene.cursor.location
    chart.rotation_euler = bpy.context.scene.cursor.rotation_euler
    target_collection.objects.link(chart)
    legend = bpy.data.objects.new("QuickChartLegend", None)
    legend.empty_display_type = 'ARROWS'
    legend.location = bpy.context.scene.cursor.location
    cr = bpy.context.scene.cursor.rotation_euler
    legend.rotation_euler = (cr[0], cr[1], cr[2] - np.pi / 2)

    target_collection.objects.link(legend)


    return { "collection": target_collection, "chart": chart, "legend": legend }



def setup_scene(target, props):
    target_obj = target["chart"]
    target_loc = (target_obj.location[0] + props.size[0]/2, target_obj.location[1] + props.size[1]/2, target_obj.location[2] + props.size[2]/2)

    world = bpy.context.scene.world
    world.use_nodes = True

    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0, 0, 0, 1)  # Schwarz
    bg.inputs["Strength"].default_value = 1.0

    ortho_scale = (max(props.size) ** 2) / 2
    create_camera(target, "QuickChartCam", (props.size[0]*2, -props.size[1]*2, props.size[2]*2), target_loc, ortho_scale=ortho_scale)

    create_area_light(
        target,
        "QuickChart_Key_Light",
        location=(props.size[0] + 6, -props.size[1], props.size[2]/2),
        target_loc=target_loc,
        power=10000,
        size=max(props.size)*2
    )

    create_area_light(
        target,
        "QuickChart_Fill_Light",
        location=(-props.size[0], props.size[1]-4, props.size[2]+4),
        target_loc = target_loc,
        power=6000,
        size=max(props.size)*2
    )

    create_area_light(
        target,
        "QuickChart_Rim_Light",
        location=(0, props.size[1] + 6, props.size[2] + 5),
        target_loc = target_loc,
        power=4000,
        size=max(props.size)*2
    )

    #create_area_light(target, name="QuickChart_Top_Light", location=(props.size[0]/2, props.size[1]/2, props.size[2]*2), target_loc=target_loc, power=1000, size=max(props.size))


def format_value_label(props, val, x, y, transposed):
    if props.data_series in {'rows'}:
        c = x if transposed else y
    else:
        c = y if transposed else x
    item = props.cell_types[c] if c is not None and c < len(props.cell_types) else None
    if item is not None:
        precision = item.precision
        cell_type = item.cell_type
    else:
        cell_type = get_cell_type(f"{val}")
        precision = 2
    if cell_type == 'label': return f"{val}"
    if cell_type == 'int': return f"{int(val)}" if -1000000 < val <  1000000 else f"{int(val):.{precision}E}"
    return f"{val:.{precision}f}" if -1000000 < val < 1000000 and not (-0.01 < val < 0.01) else f"{val:.{precision}E}"

def get_value_from_data(data):
    try:
        val = float(data)
    except ValueError:
        val = 0.0
    return val

def get_data_column_count(props, data, transposed):
    column_count = len(data[0])
    if not transposed and props.csv_format in {'left', 'header-left'}: column_count -= 1
    if transposed and props.csv_format in {'header', 'header-left'}: column_count -= 1
    return column_count

def get_data_row_count(props, data, transposed):
    row_count = len(data)
    if not transposed and props.csv_format in {'header','header_left'}: row_count -=1
    if transposed and props.csv_format in {'left', 'header-left'}: row_count -= 1
    return row_count

def show_params_and_result(func):
    """ Decorator to print function parameters and results to the console."""
    def show(*arg,**kwargs):
        res=func(*arg,**kwargs)
        print(f"{func}({arg},{kwargs}) = {res}")
        return res
    return show

def get_labels(data, labels_left = False, labels_header = False):
    if labels_left and labels_header:
        return data[0][1:]
    elif labels_header:
        return data[0]
    return list(range(1, len(data[0])))

def get_labels_invert(data, labels_left = False, labels_header = False):
    if labels_left and labels_header:
        return [ data[i][0] for i in range(1, len(data)) ]
    elif labels_left:
        return [ data[i][0] for i in range(0, len(data)) ]
    return list(range(1, len(data)))

def render_legend(target, props, labels, mats, label_mat):
    space = 1.1
    loc = bpy.context.scene.cursor.location
    target["legend"].location = (loc[0] + props.size[0] * space, loc[1], loc[2])
    for idx, label in enumerate(labels):
        loc = (loc[0] - space, loc[1], loc[2])
        zoffset =  space / 4
        if props.chart_type in {'bar','column'}:
            obj = get_object_from_shape(props.bc_shape, mats[idx])
        elif props.chart_type in {'donut'}:
            zoffset = 0
            obj = get_donut_object_from_shape(props.donut_shape, mats[idx], 0.4, 0.2, 2*np.pi )
        else:
            obj = create_bar(mats[idx])
        render_object(target["collection"], target["legend"], obj, loc=( loc[0] + space/2, loc[1] + space/2, loc[2] + zoffset), scale=(space * .8 , space * .8, space/2.2))
        render_text_object(target["collection"], target["legend"], f"{label}", (loc[0], loc[1] + space * 1.3, loc[2] + zoffset), label_mat, size=space, x_align="LEFT", y_align="TOP")

def render_column_chart(target, props, csv):
    cx, cy, cz = bpy.context.scene.cursor.location
    ph = np.pi / 2
    transposed = props.data_series == 'columns'
    data = csv["rows"] if not transposed else list(map(list, zip(*csv["rows"])))
    row_count = get_data_row_count(props, data, transposed)
    col_count = get_data_column_count(props, data, transposed)
    labels_left = (not transposed and props.csv_format in {'left', 'header-left'}) or (transposed and props.csv_format in {'header', 'header-left'})
    labels_header = (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'header-left', 'left'})

    mats = [create_material(get_color(i), roughness=props.roughness, metallic=props.metallic, alpha=props.alpha) for i in range(row_count)]
    if props.bc_sub_type in {'normal','deep'}:
        objects = [get_object_from_shape(props.bc_shape, mats[i]) for i in range(row_count)]

    space = min(props.size[0], props.size[1])
    xspace = min(space / col_count, space / row_count)
    yspace = xspace

    label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)
    value_mat = create_material(props.value_color, roughness=props.value_roughness, metallic=props.value_metallic)
    minv = min(0, csv["minv"])
    zero_z_position = remap(0, minv, csv["maxv"], 0, props.size[2])
    if props.legend: render_legend(target, props, get_labels_invert(data, labels_left=labels_left, labels_header=labels_header), mats, label_mat)

    if props.bc_sub_type == 'normal':
        xs_space = xspace / len(data) - props.spacing[0] # space 4 all
        col_idx = 0
        for col in range(len(data[0])):
            if col == 0 and labels_left: continue  # skip label
            row_idx = 0
            for row in range(len(data)):
                if row == 0 and labels_header:
                    if props.labels:
                        render_text_object(target["collection"], target["chart"], data[0][col],
                                           (cx + col_idx * xspace + xspace/2, cy - yspace/2, cz + zero_z_position), label_mat, size= xspace/2)
                    continue  # skip label

                loc = (cx + col_idx * xspace + row * xs_space, cy, cz + zero_z_position)
                val = get_value_from_data(data[row][col])
                valstr = format_value_label(props, val, col, row, transposed)
                zscale = remap(val, minv, csv["maxv"], 0, props.size[2]) - zero_z_position
                clone_and_scale_object(target, objects[row_idx], (xs_space, xs_space, zscale), loc)
                if props.values:
                    render_text_object(target["collection"], target["chart"], valstr,
                                       (loc[0], loc[1], cz + zero_z_position + (zscale if val > 0 else 0)),
                                       value_mat, size = xs_space/2.5 * 3/len(valstr), x_align='CENTER', y_align='BOTTOM', rot=(ph, 0, 0) )
                row_idx += 1
            col_idx += 1
    elif props.bc_sub_type == 'deep':
        if labels_left: cx -= xspace / 2
        col_idx = 0
        for col in range(len(data[0])):
            row_idx = 0
            for row in range(len(data)):
                loc = (cx + col_idx * xspace, cy + row_idx * yspace, cz + zero_z_position)
                if col == 0 and labels_left:
                    if props.labels:
                        srow = row
                        if labels_header: srow -= 1
                        render_text_object(target["collection"], target["chart"], data[row][col],
                                           (cx + (col_count+1) * xspace, cy + srow * yspace, loc[2]),
                                           label_mat, size = xspace/2, rot=(0,0,0), x_align='LEFT', y_align='CENTER')
                    continue  # skip label
                if row == 0 and labels_header:
                    if props.labels:
                        render_text_object(target["collection"], target["chart"], data[row][col],
                                           (loc[0], cy - yspace, loc[2]),
                                           label_mat, size = xspace/2, y_align='CENTER', )
                    continue # skip label

                val = get_value_from_data(data[row][col])
                valstr = format_value_label(props, val, col, row, transposed)
                zscale = remap(val, minv, csv["maxv"], 0, props.size[2]) - zero_z_position
                clone_and_scale_object(target, objects[row_idx], (xspace - props.spacing[0]*2, yspace - props.spacing[1]*2, zscale), loc)
                if props.values:
                    render_text_object(target["collection"], target["chart"], valstr,
                                       (loc[0], loc[1], cz + zero_z_position + (zscale if val > 0 else 0)),
                                       value_mat, size = xspace/2.5 * 2/len(valstr), x_align='CENTER', y_align='BOTTOM', rot=(ph, 0, 0) )
                row_idx += 1
            col_idx += 1
    elif props.bc_sub_type in {'stacked','percstacked'}:
        sums = csv["row_sums"] if transposed else csv["col_sums"]
        abs_sums = csv["abs_row_sums"] if transposed else csv["abs_col_sums"]
        cx += xspace/2
        col_idx = 0
        for col in range(len(data[0])):
            if abs_sums[col] != sums[col]:  # skip
                col_idx += 1
                continue

            if col == 0 and labels_left: continue  # skip label
            row_idx = 0
            lastz = 0
            zscale = remap(sums[col], min(sums), max(sums), 0, props.size[2]) - zero_z_position if props.bc_sub_type == 'stacked' else props.size[2] - zero_z_position

            if props.values and props.bc_sub_type == 'stacked':
                valstr = format_value_label(props, sums[col], col, None, transposed)
                render_text_object(target["collection"], target["chart"], valstr,
                                   (cx + col_idx * xspace, cy, cz + zero_z_position + (zscale if sums[col] > 0 else 0) ), value_mat,
                                   size = xspace/2.5 * 2/len(valstr), x_align='CENTER', y_align='BOTTOM', rot=(ph, 0, 0) )
            for row in range(len(data)):
                if row == 0 and labels_header:
                    if props.labels:
                        render_text_object(target["collection"], target["chart"], data[row][col],
                                        (cx + col_idx * xspace, cy - yspace, cz + zero_z_position), label_mat, y_align='CENTER', size = xspace/2)
                    continue  # skip label
                val = get_value_from_data(data[row][col])
                perc = val / sums[col]
                height = zscale * perc
                loc = (cx + col_idx * xspace, cy, cz + zero_z_position + lastz)
                create_stacked_object(target, props.bc_shape, mats[row_idx], loc, (xspace - props.spacing[0]*2, xspace - props.spacing[1]*2, height), height, lastz, zscale)
                lastz += height
                row_idx += 1
            col_idx += 1

def render_bar_chart(target, props, csv):
    cx, cy, cz = bpy.context.scene.cursor.location
    ph = np.pi / 2
    transposed = props.data_series == 'columns'
    data = csv["rows"] if not transposed else list(map(list, zip(*csv["rows"])))
    row_count = get_data_row_count(props, data, transposed)
    col_count = get_data_column_count(props, data, transposed)
    labels_left = (not transposed and props.csv_format in {'left', 'header-left'}) or (transposed and props.csv_format in {'header', 'header-left'})
    labels_header = (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'header-left', 'left'})

    mats = [create_material(get_color(i), roughness=props.roughness, metallic=props.metallic, alpha=props.alpha) for i in range(row_count)]
    if props.bc_sub_type in {'normal', 'deep'}:
        objects = [get_object_from_shape(props.bc_shape, mats[i]) for i in range(row_count)]

    yspace = min(props.size[1] / row_count, props.size[2] / col_count)
    zspace = yspace

    label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)
    value_mat = create_material(props.value_color, roughness=props.value_roughness, metallic=props.value_metallic)
    minv = min(0, csv["minv"])
    zero_x_position = remap(0, minv, csv["maxv"], 0, props.size[0])
    if props.legend: render_legend(target, props, get_labels_invert(data, labels_left = labels_left, labels_header = labels_header), mats, label_mat)

    if props.bc_sub_type == 'normal':
        zs_space = zspace / len(data) - props.spacing[2]  # space 4 all
        col_idx = 0
        for col in range(len(data[0])):
            if col == 0 and labels_left: continue  # skip label
            row_idx = 0
            for row in range(len(data)):
                if row == 0 and labels_header:
                    if props.labels:
                        render_text_object(target["collection"], target["chart"], data[0][col],
                                           (cx +zero_x_position, cy - yspace / 2, cz + col_idx * zspace + zspace / 2),
                                           label_mat, size=zspace / 2, x_align="RIGHT", y_align="CENTER", rot=(ph, 0, ph))
                    continue  # skip label

                loc = (cx + zero_x_position, cy, cz  + col_idx * zspace + row * zs_space)
                val = get_value_from_data(data[row][col])
                valstr = format_value_label(props, val, col, row, transposed)
                xscale = remap(val, minv, csv["maxv"], 0, props.size[0]) - zero_x_position
                clone_and_scale_object(target, objects[row_idx], (zs_space, zs_space, xscale), loc, rot=(0, ph, 0))
                if props.values:
                    render_text_object(target["collection"], target["chart"], valstr,
                                       (cx + zero_x_position + (xscale if val > 0 else 0), loc[1], loc[2]),
                                       value_mat, size=zs_space / 2.5 * 3 / len(valstr), x_align='LEFT', y_align='CENTER', rot=(ph, 0, 0))
                row_idx += 1
            col_idx += 1
    elif props.bc_sub_type == 'deep':
        if labels_left: cz -= zspace / 2
        col_idx = 0
        for col in range(len(data[0])):
            row_idx = 0
            for row in range(len(data)):
                loc = (cx + zero_x_position, cy + row_idx * yspace, cz + col_idx * zspace, )
                if col == 0 and labels_left:
                    if props.labels:
                        srow = row
                        if labels_header: srow -= 1
                        render_text_object(target["collection"], target["chart"], data[row][col],
                                           (loc[0], cy + srow * yspace, cz + (col_count + 1) * zspace),
                                           label_mat, size=zspace / 2, rot=(ph, ph, ph), x_align='RIGHT', y_align='CENTER')
                    continue  # skip label
                if row == 0 and labels_header:
                    if props.labels:
                        render_text_object(target["collection"], target["chart"], data[row][col],
                                           (loc[0], cy - yspace, loc[2]),
                                           label_mat, size=zspace / 2, x_align='LEFT', y_align='CENTER', rot = (ph, 0, ph))
                    continue  # skip label

                val = get_value_from_data(data[row][col])
                valstr = format_value_label(props, val, col, row, transposed)
                xscale = remap(val, minv, csv["maxv"], 0, props.size[0]) - zero_x_position
                clone_and_scale_object(target, objects[row_idx], (zspace - props.spacing[0] * 2, yspace - props.spacing[1] * 2, xscale), loc, rot=(0, ph, 0))
                if props.values:
                    render_text_object(target["collection"], target["chart"], valstr,
                                       (cx + zero_x_position + (xscale if val > 0 else 0), loc[1], loc[2]),
                                       value_mat, size=zspace / 2.5 * 2 / len(valstr), x_align='LEFT', y_align='CENTER', rot=(ph, 0, 0))
                row_idx += 1
            col_idx += 1
    elif props.bc_sub_type in {'stacked', 'percstacked'}:
        sums = csv["row_sums"] if transposed else csv["col_sums"]
        abs_sums = csv["abs_row_sums"] if transposed else csv["abs_col_sums"]
        cz += zspace / 2
        col_idx = 0
        for col in range(len(data[0])):
            if abs_sums[col] != sums[col]:  # skip
                col_idx += 1
                continue

            if col == 0 and labels_left: continue  # skip label
            row_idx = 0
            lastx = 0
            xscale = remap(sums[col], min(sums), max(sums), 0, props.size[0]) - zero_x_position if props.bc_sub_type == 'stacked' else props.size[0] - zero_x_position

            if props.values and props.bc_sub_type == 'stacked':
                valstr = format_value_label(props, sums[col], col, None, transposed)
                render_text_object(target["collection"], target["chart"], valstr,
                                   (cx + zero_x_position + (xscale if sums[col] > 0 else 0), cy, cz  + col_idx * zspace ), value_mat,
                                   size=zspace / 2.5 * 2 / len(valstr), x_align='LEFT', y_align='CENTER', rot=(ph, 0, 0))
            for row in range(len(data)):
                if row == 0 and labels_header:
                    if props.labels:
                        render_text_object(target["collection"], target["chart"], data[row][col],
                                           (cx + zero_x_position, cy - yspace, cz  + col_idx * zspace), label_mat, y_align='CENTER', size=zspace / 2, rot =(ph, 0, ph))
                    continue  # skip label
                val = get_value_from_data(data[row][col])
                perc = val / sums[col]
                width = xscale * perc
                loc = (cx + zero_x_position + lastx, cy, cz + col_idx * zspace)
                create_stacked_object(target, props.bc_shape, mats[row_idx], loc,
                                      (zspace - props.spacing[0] * 2, zspace - props.spacing[1] * 2, width),
                                      width, lastx, xscale, rot=(0, ph, 0))
                lastx += width
                row_idx += 1
            col_idx += 1

def render_donut_chart(target, props, csv):
    cx, cy, cz = bpy.context.scene.cursor.location
    ph = np.pi / 2
    tp = np.pi * 2
    transposed = props.data_series == 'columns'
    labels_left = (not transposed and props.csv_format in {'left', 'header-left'}) or (transposed and props.csv_format in {'header', 'header-left'})
    labels_header = (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'header-left', 'left'})


    if props.values: value_mat = create_material(props.value_color, roughness=props.value_roughness, metallic=props.value_metallic)

    data = csv["rows"] if not transposed else list(map(list, zip(*csv["rows"])))
    mats = [create_material(get_color(i), roughness=props.roughness, metallic=props.metallic, alpha=props.alpha) for i in range(len(data[0]))]
    sums = csv["col_sums"] if transposed else csv["row_sums"]
    abs_sums = csv["abs_col_sums"] if transposed else csv["abs_row_sums"]

    r = min(props.size[0]/2, props.size[2] /2)
    r1 = r/10
    row_count = get_data_row_count(props, data, transposed)
    rs = - (r - r1) / row_count # ring space
    if row_count == 1: rs = - r / 2
    rsh = rs / 2 # half ring space
    text_size = abs(rsh) * 1.5
    gap = min(props.spacing[0], props.spacing[2])
    donut_radius = abs(rsh) - gap
    last_radius = r

    if props.legend:
        label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)
        render_legend(target, props, get_labels(data, labels_left = labels_left, labels_header = labels_header), mats, label_mat)
        target["legend"].rotation_euler = (0, ph, -ph)

    loc = (cx + props.size[0] / 2, cy, cz + props.size[2] / 2)
    for row in range(len(data)):

        col_idx = 0
        if row == 0 and labels_header: continue
        last_angle = ph
        if abs_sums[row] != sums[row]:
            last_radius += rs
            continue
        for col in range(len(data[0])):
            if col == 0 and labels_left: continue
            val = get_value_from_data(data[row][col])
            perc = val / sums[row]
            angle = tp * perc
            obj = get_donut_object_from_shape(props.donut_shape, mats[col_idx], last_radius + rsh, donut_radius, angle)
            render_object(target["collection"], target["chart"], obj, loc=loc, rot=(ph, -last_angle, 0))
            if props.values:
                val_str = format_value_label(props, val, col, row, transposed)
                label_angle = angle / 2 + last_angle
                label_radius = last_radius + rsh
                render_text_object(target["collection"], target["chart"],
                                   val_str,
                                   (loc[0] + label_radius * np.cos(label_angle), loc[1] - abs(rsh), loc[2] + label_radius * np.sin(label_angle)),
                                   value_mat, rot=(ph, 0, 0),
                                   size= text_size / len(val_str),
                                   x_align="CENTER", y_align="CENTER")
            col_idx += 1
            last_angle += angle
        last_radius += rs
def get_dimensions(obj):
    bbox = [Vector(v) for v in obj.bound_box]
    return (
        max(v.x for v in bbox) - min(v.x for v in bbox),
        max(v.y for v in bbox) - min(v.y for v in bbox),
        max(v.z for v in bbox) - min(v.z for v in bbox)
    )
def render_table(target, props, csv):
    ph = np.pi / 2
    pq = np.pi / 4
    cx, cy, cz = bpy.context.scene.cursor.location
    transposed = props.data_series == 'columns'
    data = csv["rows"] if not transposed else list(map(list, zip(*csv["rows"])))
    labels_left = (not transposed and props.csv_format in {'left', 'header-left'}) or (transposed and props.csv_format in {'header', 'header-left'})
    labels_header = (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'header-left', 'left'})
    xspace = props.size[0] / len(data[0])
    zspace = props.size[2] / len(data)
    label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)
    value_mat = create_material(props.value_color, roughness=props.value_roughness, metallic=props.value_metallic)

    for row_idx, row in enumerate(data):
        for col_idx, cell in enumerate(row):
            loc = (cx + xspace * col_idx, cy, cz + props.size[2] - zspace * row_idx)
            rot = [ph, 0, 0]
            val = cell
            x_align = 'CENTER'
            size = min(xspace, zspace) * 0.5 - min(props.spacing[0], props.spacing[2])
            if row_idx == 0 and labels_header:
                if not props.labels: continue
                rot[1] = -ph/2
                x_align = 'LEFT'
                mat = label_mat
                loc = (cx + xspace/2 + xspace * col_idx, cy, cz + props.size[2] - zspace * row_idx)

            elif col_idx == 0 and labels_left:
                if not props.labels: continue
                mat = label_mat
            else:
                if not props.values: continue
                val = format_value_label(props, get_value_from_data(cell), col_idx, row_idx, transposed)
                size = min(xspace, zspace) * .8 / len(val) - min(props.spacing[0], props.spacing[2])
                mat = value_mat

            obj = render_text_object(target["collection"], target["chart"], val, loc, mat, size=size, x_align = x_align, y_align = 'CENTER', rot=rot)
            if row_idx == 0 and labels_header and col_idx < len(row)-1: # header bars
                render_object(target["collection"], target["chart"],
                              create_cylinder(label_mat),
                              rot=(0, pq, 0),
                              loc=(cx + xspace * col_idx + xspace / 2, loc[1], loc[2] - zspace / 2),
                              scale=(0.1, 0.1, xspace /2 + get_dimensions(obj)[0]))
            elif col_idx < len(row) - 1: # vertical bars
                render_object(target["collection"], target["chart"],
                          create_cylinder(label_mat),
                          loc=(loc[0] + xspace/2, loc[1], loc[2] - zspace/2),
                          scale=(0.1, 0.1, zspace))
            if (not labels_header or row_idx > 0) and row_idx < len(data) - 1: # horizontal bars
                barloc = (loc[0] - xspace/2, loc[1], loc[2] - zspace / 2)
                scale = (0.1, 0.1, xspace)
                if col_idx == 0 and labels_left:
                    scale = (0.1, 0.1, max(xspace, get_dimensions(obj)[0]))
                    barloc = (loc[0] - scale[2] /2, barloc[1], barloc[2])
                render_object(target["collection"], target["chart"],
                              create_cylinder(label_mat),
                              loc=barloc,
                              rot=(0, ph, 0),
                              scale=scale)
def render_line_chart(target, props, csv):
    cx, cy, cz = bpy.context.scene.cursor.location
    ph = np.pi / 2
    transposed = props.data_series == 'columns'
    data = csv["rows"] if not transposed else list(map(list, zip(*csv["rows"])))
    row_count = get_data_row_count(props, data, transposed)
    col_count = get_data_column_count(props, data, transposed)
    labels_left = (not transposed and props.csv_format in {'left', 'header-left'}) or (transposed and props.csv_format in {'header', 'header-left'})
    labels_header = (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'header-left', 'left'})

    mats = [create_material(get_color(i), roughness=props.roughness, metallic=props.metallic, alpha=props.alpha) for i in range(row_count)]
    x_space = props.size[0] / len(data[0])
    label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)
    value_mat = create_material(props.value_color, roughness=props.value_roughness, metallic=props.value_metallic)
    minv = min(0, csv["minv"])
    zero_z_position = remap(0, minv, csv["maxv"], 0, props.size[2])
    if props.legend:
        render_legend(target, props, get_labels_invert(data, labels_left = labels_left, labels_header = labels_header), mats, label_mat)
        target["legend"].rotation_euler = (0, ph, -ph)

    row_idx = 0
    for row in range(len(data)):
        if row == 0 and labels_header:
            if props.labels:
                for col in range(len(data[row])):
                    loc = (cx + col * x_space, cy, cz + zero_z_position )
                    render_text_object(target["collection"], target["chart"],
                                       data[row][col], loc, label_mat, size=x_space/2, x_align="RIGHT", y_align='CENTER',
                                       rot=(ph, -np.pi/4, 0))
            continue
        loc = (cx + x_space if labels_left else 0, cy + row_idx * 0.2, cz + zero_z_position)
        row_data = data[row][1:] if labels_left else data[row]
        obj = create_line_chart(mats[row_idx], row_data, x_space, minv, csv["maxv"], 0, props.size[2], zero_z_position)
        render_object(target["collection"], target["chart"], obj, loc=loc)
        row_idx += 1

def render_chart(props, csv):
    np.random.seed(0)
    target  = init_target_collection()
    setup_scene(target, props)
    if props.chart_type == "column":
        render_column_chart(target , props, csv)
    elif props.chart_type == "bar":
        render_bar_chart(target, props, csv)
    elif props.chart_type == "donut":
        render_donut_chart(target, props, csv)
    elif props.chart_type == "table":
        render_table(target, props, csv)
    elif props.chart_type == "line":
        render_line_chart(target, props, csv)