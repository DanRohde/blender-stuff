import bpy
import bmesh
import numpy as np

from .constants import COLORS

def create_object(name, mesh, mat):
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    return obj

def clone_and_scale_object(target, obj, scale, loc, rot = (0,0,0)):
    new_obj = bpy.data.objects.new(name=obj.name, object_data=obj.data)
    mw = new_obj.matrix_world.copy()
    new_obj.parent = target["chart"]
    new_obj.matrix_world = mw

    new_obj.scale = scale
    new_obj.location = loc
    new_obj.rotation_euler = rot
    new_obj.hide_viewport = False
    target["collection"].objects.link(new_obj)
    return new_obj

def hide_object(obj):
    obj.hide_viewport = True

def origin_to_bottom(bm):
    min_z = min(v.co.z for v in bm.verts)

    for v in bm.verts:
        v.co.z -= min_z

def create_bar(mat):
    name = "QuickChartBar"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size = 1 )
    origin_to_bottom(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return create_object(name, mesh, mat)

def create_cylinder(mat):
    name = "QuickChartCylinder"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=128, radius1=.5, radius2=.5, depth=1, cap_ends=True)
    origin_to_bottom(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return create_object(name, mesh, mat)

def create_cone(mat, r1=.5, r2=0, depth=1):
    name = "QuickChartCone"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=128, radius1=r1, radius2=r2, depth=depth, cap_ends=True)
    origin_to_bottom(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return create_object(name, mesh, mat)

def create_pyramid(mat, base_size = 1):
    name = "QuickChartPyramid"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    half = base_size / 2
    v0 = bm.verts.new((-half, -half, 0))
    v1 = bm.verts.new(( half, -half, 0))
    v2 = bm.verts.new(( half,  half, 0))
    v3 = bm.verts.new((-half,  half, 0))
    top = bm.verts.new((0, 0, 1))

    bm.faces.new((v0, v1, v2, v3))
    bm.faces.new((v0, v1, top))
    bm.faces.new((v1, v2, top))
    bm.faces.new((v2, v3, top))
    bm.faces.new((v3, v0, top))

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return create_object(name, mesh, mat)

def create_pyramid_frustam(mat, base_size = 1, top_size = 1):
    name="QuickChartPyramidFrustam"
    height = 1

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    b1 = bm.verts.new((-base_size / 2, -base_size / 2, 0))
    b2 = bm.verts.new((base_size / 2, -base_size / 2, 0))
    b3 = bm.verts.new((base_size / 2, base_size / 2, 0))
    b4 = bm.verts.new((-base_size / 2, base_size / 2, 0))

    t1 = bm.verts.new((-top_size / 2, -top_size / 2, height))
    t2 = bm.verts.new((top_size / 2, -top_size / 2, height))
    t3 = bm.verts.new((top_size / 2, top_size / 2, height))
    t4 = bm.verts.new((-top_size / 2, top_size / 2, height))

    bm.faces.new((b1, b2, b3, b4))
    bm.faces.new((t1, t2, t3, t4))

    bm.faces.new((b1, b2, t2, t1))
    bm.faces.new((b2, b3, t3, t2))
    bm.faces.new((b3, b4, t4, t3))
    bm.faces.new((b4, b1, t1, t4))

    bm.to_mesh(mesh)
    bm.free()

    return create_object(name, mesh, mat)

def create_material(color, roughness = 0.5, metallic = 0, alpha = None):
    mat = bpy.data.materials.new("QuickChartMat1")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha if alpha is not None else color[3]
    return mat

def render_text_object(collection, parent, text, loc, mat, rot = (0, 0, np.pi / 2), x_align = 'RIGHT', y_align = 'BOTTOM', size = 1):
    name = f"Label {text}"
    text_data = bpy.data.curves.new(name=name,type='FONT')
    text_data.body = text
    text_data.size = size
    text_data.extrude = .02 * size
    text_data.bevel_depth = 0.03 * size
    text_data.bevel_resolution = 4
    text_data.align_x = x_align
    text_data.align_y = y_align
    #text_data.font = bpy.data.fonts.load(font_path)

    text_obj = bpy.data.objects.new(name=name, object_data = text_data)
    text_obj.location = loc
    text_obj.rotation_euler = rot
    text_obj.parent = parent
    collection.objects.link(text_obj)
    text_obj.data.materials.append(mat)

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

def get_color(color_idx):
    if color_idx > len(COLORS)-1:
        color = np.random.rand(4)
        color[3] = 1
    else:
        color = COLORS[color_idx]
    return color

def get_object_from_shape(shape, mat):
    if shape == 'cone': obj = create_cone(mat)
    elif shape == 'cylinder': obj = create_cylinder(mat)
    elif shape == 'pyramid': obj = create_pyramid(mat)
    else: obj = create_bar(mat)
    return obj

def create_stacked_object(target, shape, mat, loc, scale, val, height, maxv, rot=(0, 0, 0)):

    if shape == 'cone':
        if maxv != 0:
            r1 = (maxv-height) * 0.5/maxv
            r2 = (maxv-height-val) * 0.5/maxv
            obj = create_cone(mat,r1=r1,r2=r2)
        else:
            obj = create_cone(mat)
    elif shape == 'cylinder':
        obj = create_cylinder(mat)
    elif shape == 'pyramid':
        if maxv != 0:
            bs = (maxv-height)/maxv
            ts = (maxv-height-val)/maxv
            obj = create_pyramid(mat, base_size=bs) if ts == 0 else create_pyramid_frustam(mat, bs, ts)
        else:
            obj = create_pyramid(mat)
    else:
        obj = create_bar(mat)

    obj.parent = target["chart"]
    obj.scale = scale
    obj.data.materials.append(mat)
    obj.location = loc
    obj.rotation_euler = rot
    target["collection"].objects.link(obj)


def remap(x, in_min, in_max, out_min, out_max):
    return out_min + ((x - in_min) / (in_max - in_min)) * (out_max - out_min)

def format_value_label(props, val, x, y, transposed):
    c = y if transposed else x
    item = props.column_types[c] if c is not None else None
    if item is not None:
        precision = item.precision
        column_type = item.column_type
    else:
        column_type = "int" if int(val) == val else "float"
        precision = 2

    if column_type == 'int': return f"{int(val)}" if -1000000 < val <  1000000 else f"{int(val):.{precision}E}"
    return f"{val:.{precision}f}" if -1000000 < val < 1000000 and not (-0.01 < val < 0.01) else f"{val:.{precision}E}"

def get_value_from_data(data):
    try:
        val = float(data)
    except ValueError:
        val = 0.0
    return val
def render_legend(target, props, data, mats, label_mat, label_size, transposed):
    loc = bpy.context.scene.cursor.location
    labels = [ row[0] for row in data ]
    space = label_size * 1.1

    label_len = [ len(label) for label in labels ]
    loc = (loc[0] - space * (1+len(labels)), loc[1] + props.size[1], loc[2])
    render_text_object(target["collection"], target["legend"], "Legend", loc, label_mat, size = space, x_align="LEFT", y_align="TOP")
    color_idx = 0
    for idx, label in enumerate(labels):
        if idx==0 and props.csv_format in {'header-left', 'header'} and not transposed: continue
        if idx==0 and props.csv_format in {'header-left', 'left'} and transposed: continue
        loc = (loc[0] + space, loc[1], loc[2])
        obj = get_object_from_shape(props.bc_shape, mats[color_idx]) if props.chart_type in {'bar','column'} else create_bar(mats[color_idx])
        obj.parent = target["legend"]
        obj.scale = (space * .8 , space * .8, space/2.2)
        obj.location = ( loc[0] + space/2, loc[1] + space/2, loc[2] - space/4)
        target["collection"].objects.link(obj)
        if (not transposed and props.csv_format in {'header-left', 'left'}) or (transposed and props.csv_format in {'header-left','header'}):
            text = label
        else:
            text = f"{color_idx+1}"
        render_text_object(target["collection"], target["legend"], text, (loc[0], loc[1] + space * 1.3, loc[2]), label_mat, size=space, x_align="LEFT", y_align="TOP")
        color_idx += 1


def render_column_chart(target, props, csv):
    cx, cy, cz = bpy.context.scene.cursor.location
    transposed = props.data_series == 'columns'
    data = csv["rows"] if not transposed else list(map(list, zip(*csv["rows"])))
    mats = [create_material(get_color(i), roughness=props.roughness, metallic=props.metallic, alpha=props.alpha) for i in range(len(data))]
    if props.bc_sub_type in {'normal','deep'}:
        objects = [get_object_from_shape(props.bc_shape, mats[i]) for i in range(len(data))]

    maxcolumns  = len(data[0])
    if not transposed and props.csv_format in {'header-left', 'left'}: maxcolumns+=1
    if transposed and props.csv_format in {'header-left','header'}: maxcolumns+=1
    xspace = props.size[0] / maxcolumns
    label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)
    minv = min(0, csv["minv"])
    zero_z_position = remap(0, minv, csv["maxv"], 0, props.size[2])
    if props.legend: render_legend(target, props, data, mats, label_mat, xspace/2, transposed)

    if props.bc_sub_type == 'normal':
        xs_space = xspace / len(data) - props.spacing[0] # space 4 all
        columnidx = 0
        for x in range(len(data[0])):
            if x == 0:
                if ((not transposed and props.csv_format in {'left', 'header-left'})
                        or (transposed and props.csv_format in {'header','header-left'} )):
                    continue  # skip label
            color_idx = 0
            for xs in range(len(data)):
                if xs == 0:
                    if (not transposed and props.csv_format in {'header','header-left'}) or (transposed and props.csv_format in {'left','header-left'}):
                        if props.labels: render_text_object(target["collection"], target["chart"], data[0][x], (cx + columnidx * xspace + xspace/2, cy - xspace/2, cz + zero_z_position), label_mat, size= xspace/2)
                        continue  # skip label

                loc = (cx + columnidx * xspace + xs * xs_space, cy, cz + zero_z_position)
                val = get_value_from_data(data[xs][x])
                valstr = format_value_label(props, val, x, xs, transposed)
                zscale = remap(val, minv, csv["maxv"], 0, props.size[2]) - zero_z_position
                clone_and_scale_object(target, objects[color_idx], (xs_space, xs_space, zscale), loc)
                color_idx += 1
                if props.values: render_text_object(target["collection"], target["chart"], valstr, (loc[0], loc[1], cz + zero_z_position + (zscale if val > 0 else 0)), label_mat, size = xs_space/2.5 * 3/len(valstr), x_align='CENTER', y_align='BOTTOM', rot=(np.pi/2,0,0) )
            columnidx += 1
    elif props.bc_sub_type == 'deep':
        maxrows = max(len(data[0]),len(data))
        yspace = props.size[1] / maxrows
        columnidx = 0
        for x in range(len(data[0])):
            color_idx = 0

            for y in range(len(data)):
                if x == 0:
                    if (not transposed and props.csv_format in {'left', 'header-left'}) or (transposed and props.csv_format in {'header','header-left'}):
                        if props.labels: render_text_object(target["collection"], target["chart"], data[y][x], (cx + len(data[0]) * xspace, cy + y * yspace, cz + zero_z_position), label_mat, size = xspace/2, rot=(0,0,0), x_align='LEFT', y_align='CENTER')
                        continue  # skip label
                if y == 0:
                    if (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'header-left', 'left'}):
                        if props.labels: render_text_object(target["collection"], target["chart"], data[0][x], (cx + columnidx * xspace, cy, cz + zero_z_position ), label_mat, y_align='CENTER', size = xspace/2)
                        continue # skip label
                loc = (cx + columnidx * xspace, cy + y * yspace, cz + zero_z_position)
                val = get_value_from_data(data[y][x])
                valstr = format_value_label(props, val, x, y, transposed)
                zscale = remap(val, minv, csv["maxv"], 0, props.size[2]) - zero_z_position
                clone_and_scale_object(target, objects[color_idx], (xspace - props.spacing[0]*2, yspace - props.spacing[1]*2, zscale), loc)
                color_idx += 1
                if props.values: render_text_object(target["collection"], target["chart"], valstr, (loc[0], loc[1], cz + zero_z_position + (zscale if val > 0 else 0)), label_mat, size = xspace/2.5 * 2/len(valstr), x_align='CENTER', y_align='BOTTOM', rot=(np.pi/2,0,0) )
            columnidx += 1
    elif props.bc_sub_type in {'stacked','percstacked'}:
        column_idx = 0
        sums = csv["row_sums"] if transposed else csv["col_sums"]
        abs_sums = csv["abs_row_sums"] if transposed else csv["abs_col_sums"]

        for x in range(len(data[0])):
            if x == 0:
                if ((not transposed and props.csv_format in {'left', 'header-left'})
                        or (transposed and props.csv_format in {'header','header-left'} )):
                    continue  # skip label
            color_idx = 0
            lastz = 0
            zscale = remap(sums[x], min(sums), max(sums), 0, props.size[2]) - zero_z_position if props.bc_sub_type == 'stacked' else props.size[2] - zero_z_position
            if props.values and props.bc_sub_type == 'stacked':
                valstr = format_value_label(props, sums[x], x, None, transposed)
                render_text_object(target["collection"], target["chart"], valstr,
                                   (cx + column_idx * xspace, cy, cz + zero_z_position + (zscale if sums[x] > 0 else 0) ), label_mat,
                                   size = xspace/2.5 * 2/len(valstr), x_align='CENTER', y_align='BOTTOM', rot=(np.pi/2,0,0) )
            if abs_sums[x] != sums[x]:
                clone_and_scale_object(
                    target,
                    get_object_from_shape(props.bc_shape, create_material(get_color(len(data)), roughness = props.roughness, metallic=props.metallic, alpha=props.alpha)),
                    (xspace - props.spacing[0]*2, xspace - props.spacing[1]*2, zscale ),
                    (cx + column_idx * xspace, cy, cz + zero_z_position)
                )
                column_idx += 1
                color_idx += 1
                continue
            for y in range(len(data)):
                if y == 0:
                    if (not transposed and props.csv_format in {'header','header-left'}) or (transposed and props.csv_format in {'left','header-left'}):
                        if props.labels: render_text_object(target["collection"], target["chart"], data[0][x], (cx + column_idx * xspace, cy - xspace/2, cz + zero_z_position), label_mat, y_align='CENTER', size = xspace/2)
                        continue  # skip label
                val = get_value_from_data(data[y][x])
                perc = val / sums[x]
                height = zscale * perc
                loc = (cx + column_idx * xspace, cy, cz + zero_z_position + lastz)
                create_stacked_object(target, props.bc_shape, mats[color_idx], loc, (xspace - props.spacing[0]*2, xspace - props.spacing[1]*2,height), height, lastz, zscale)
                lastz += height
                color_idx += 1
            column_idx += 1

def render_bar_chart(target, props, csv):
    cx, cy, cz = bpy.context.scene.cursor.location
    ph = np.pi / 2
    transposed = props.data_series == 'columns'
    data = csv["rows"] if not transposed else list(map(list, zip(*csv["rows"])))  # transpose csv if necessary

    maxcolumns = len(data)
    if props.csv_format in {'header-left'}: maxcolumns += 1
    if transposed and props.csv_format in {'left', 'header-left'}: maxcolumns += 1
    zspace = props.size[0] / maxcolumns
    mats = [create_material(get_color(i), roughness=props.roughness, metallic=props.metallic, alpha=props.alpha) for i in range(len(data))]
    objects = [get_object_from_shape(props.bc_shape, mats[i]) for i in range(len(data))]
    label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)

    minv = min(0, csv["minv"])
    zero_x_position = remap(0, minv, csv["maxv"], 0, props.size[0])
    if props.legend: render_legend(target, props, data, mats, label_mat, zspace/2, transposed)

    if props.bc_sub_type == 'normal':
        zs_space = zspace / len(data) - props.spacing[0]
        rowindex = 0
        for z in range(len(data[0])):
            if z == 0:
                if (not transposed and props.csv_format in {'left', 'header-left'}) or (props.csv_format in {'header', 'header-left'} and transposed):
                    continue  # skip label
            color_idx = 0
            for zs in range(len(data)):
                if zs == 0:
                    if (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'left', 'header-left'}):
                        if props.labels: render_text_object(target["collection"], target["chart"], data[0][z], (cx + zero_x_position , cy - zspace / 2, cz + rowindex * zspace + zspace / 2), label_mat, size=zspace / 2, rot=(ph, 0, ph), x_align='RIGHT', y_align='TOP')
                        continue  # skip label
                loc = (cx + zero_x_position, cy, cz + rowindex * zspace + zs * zs_space)
                try:
                    val = float(data[zs][z])
                except ValueError:
                    val = 0.0
                valstr = format_value_label(props, val, z, zs, transposed)
                xscale = remap(val, minv, csv["maxv"], 0, props.size[0]) - zero_x_position
                clone_and_scale_object(target, objects[color_idx], (zs_space, zs_space, xscale), loc, rot=(0, ph, 0))
                color_idx += 1
                if props.values: render_text_object(target["collection"], target["chart"], valstr, (cx + zero_x_position + (xscale if val > 0 else 0), loc[1], loc[2]), label_mat, size=zs_space / 2.5 * 3 / len(valstr), x_align='LEFT', y_align='CENTER', rot=(ph, 0, 0))
            rowindex += 1
    elif props.bc_sub_type == 'deep':
        maxcolumns = max(len(data), len(data[0]))
        yspace = props.size[1] / maxcolumns
        rowindex = 0
        for z in range(len(data[0])):
            color_idx = 0
            for y in range(len(data)):
                if z == 0:
                    if (not transposed and props.csv_format in {'left', 'header-left'}) or (transposed and props.csv_format in {'header', 'header-left'}):
                        if props.labels: render_text_object(target["collection"], target["chart"], data[y][z], (cx + zero_x_position, cy + y * yspace, cz + len(data[0]) * zspace), label_mat, size=zspace/2, rot=(ph, 0, ph), x_align='RIGHT' if y==0 else 'CENTER', y_align='CENTER')
                        continue  # skip label
                if y == 0:
                    if (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'header-left', 'left'}):
                        if props.labels: render_text_object(target["collection"], target["chart"], data[0][z], (cx + zero_x_position , cy, cz + rowindex * zspace ), label_mat, size=zspace/2, x_align='RIGHT', y_align='CENTER', rot=(ph, 0, ph))
                        continue  # skip label
                loc = (cx + zero_x_position , cy + y * yspace, cz + rowindex * zspace )
                try:
                    val = float(data[y][z])
                except ValueError:
                    val = 0.0
                valstr = format_value_label(props, val, z, y, transposed)
                xscale = remap(val, minv, csv["maxv"], 0, props.size[0]) - zero_x_position
                clone_and_scale_object(target, objects[color_idx], (zspace - props.spacing[0] * 2, yspace - props.spacing[1] * 2, xscale ), loc, rot=(0, ph, 0))
                color_idx += 1
                if props.values: render_text_object(target["collection"], target["chart"], valstr, (cx + zero_x_position + (xscale if val > 0 else 0), loc[1], loc[2]) , label_mat, size=zspace / 2.5 * 2 / len(valstr), x_align='LEFT', y_align='CENTER', rot=(ph, 0, 0))
            rowindex += 1
    elif props.bc_sub_type in {'stacked', 'percstacked'}:
        row_idx = 0
        sums = csv["row_sums"] if transposed else csv["col_sums"]
        abs_sums = csv["abs_row_sums"] if transposed else csv["abs_col_sums"]
        for z in range(len(data[0])):
            if z == 0:
                if ((not transposed and props.csv_format in {'left', 'header-left'})
                        or (transposed and props.csv_format in {'header', 'header-left'})):
                    continue  # skip label
            color_idx = 0
            lastx = 0
            xscale = remap(sums[z], min(sums), max(sums), 0, props.size[0]) - zero_x_position if props.bc_sub_type == 'stacked' else props.size[0] - zero_x_position
            if props.values and props.bc_sub_type == 'stacked':
                valstr = format_value_label(props, sums[z], z, None, transposed)
                render_text_object(target["collection"], target["chart"], valstr,
                                   (cx + zero_x_position + (xscale if sums[z] > 0 else 0) , cy, cz + row_idx * zspace ), label_mat,
                                   size=zspace / 2.5 * 2 / len(valstr), x_align='LEFT', y_align='BOTTOM', rot=(np.pi / 2, 0, 0))
            if abs_sums[z] != sums[z]:
                clone_and_scale_object(
                    target,
                    get_object_from_shape(props.bc_shape, create_material(get_color(len(data)), roughness=props.roughness, metallic=props.metallic, alpha=props.alpha)),
                    (zspace - props.spacing[0] * 2, zspace - props.spacing[1] * 2, xscale),
                    (cx + zero_x_position, cy, cz  + row_idx * zspace),
                    rot = (0, ph, 0)
                )
                color_idx += 1
                row_idx += 1
                continue

            for y in range(len(data)):
                if y == 0:
                    if (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'left', 'header-left'}):
                        if props.labels:
                            render_text_object(target["collection"], target["chart"], data[0][z],
                                               (cx + zero_x_position, cy - zspace / 2, cz + row_idx * zspace), label_mat, y_align='CENTER', size=zspace / 2, rot=(ph, 0, 0))
                        continue  # skip label
                val = get_value_from_data(data[y][z])
                perc = val / sums[z]
                width = xscale * perc

                loc = (cx + zero_x_position + lastx, cy, cz + row_idx * zspace)
                create_stacked_object(target, props.bc_shape, mats[color_idx], loc, (zspace - props.spacing[0] * 2, zspace - props.spacing[1] * 2, width), width, lastx, xscale, rot=(0, ph, 0))
                lastx += width
                color_idx += 1
            row_idx += 1

def render_chart(props, csv):
    np.random.seed(0)
    target  = init_target_collection()
    if props.chart_type == "column":
        render_column_chart(target , props, csv)
    elif props.chart_type == "bar":
        render_bar_chart(target, props, csv)