import bpy
import bmesh
import numpy as np
from mathutils import Vector

from .constants import COLORS
from .data import get_cell_type

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

def shade_smooth(bm):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
    angle_rad = np.radians(30)
    for e in bm.edges:
        if len(e.link_faces) != 2: continue
        f1, f2 = e.link_faces
        if f1.normal.length == 0 or f2.normal.length == 0: continue
        if f1.normal.angle(f2.normal) > angle_rad:
            e.smooth = False
        else:
            e.smooth = True

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
    bmesh.ops.create_cone(bm, segments=32, radius1=.5, radius2=.5, depth=1, cap_ends=True)
    origin_to_bottom(bm)
    shade_smooth(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return create_object(name, mesh, mat)

def create_cone(mat, r1=.5, r2=0, depth=1):
    name = "QuickChartCone"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=32, radius1=r1, radius2=r2, depth=depth, cap_ends=True)
    origin_to_bottom(bm)
    shade_smooth(bm)
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

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

#    bm.normal_update()
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

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

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

def create_partial_donat(mat, major_radius = 1.0, minor_radius = 0.3, angle=np.pi, major_segments = 32, minor_segments = 16):
    name = "QuickChartPartialDonat"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = []
    for i in range(major_segments + 1):
        phi = angle * i / major_segments
        ring = []
        for j in range(minor_segments):
            theta = 2 * np.pi * j / minor_segments

            x = (major_radius + minor_radius * np.cos(theta)) * np.cos(phi)
            y = (major_radius + minor_radius * np.cos(theta)) * np.sin(phi)
            z = minor_radius * np.sin(theta)

            ring.append(bm.verts.new((x, y, z)))

        verts.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(major_segments):
        for j in range(minor_segments):
            v1 = verts[i][j]
            v2 = verts[i][(j + 1) % minor_segments]
            v3 = verts[i + 1][(j + 1) % minor_segments]
            v4 = verts[i + 1][j]
            bm.faces.new((v1, v2, v3, v4))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    if angle != 2 * np.pi:
        bm.faces.new(verts[0])
        bm.faces.new(list(reversed(verts[-1])))

    shade_smooth(bm)

    bm.to_mesh(mesh)
    bm.free()
    return create_object(name, mesh, mat)

def create_cubic_partial_donut(mat, major_radius = 1.0, half_size = 0.3, angle=np.pi, segments = 32):
    name = "QuickChartCubicPartialDonut"

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    square = [
        (-half_size, -half_size),
        (half_size, -half_size),
        (half_size, half_size),
        (-half_size, half_size),
    ]
    rings = []
    for i in range(segments + 1):
        phi = angle * i / segments
        cos_p = np.cos(phi)
        sin_p = np.sin(phi)

        ring = []
        for x, z in square:
            X = (major_radius + x) * cos_p
            Y = (major_radius + x) * sin_p
            Z = z
            ring.append(bm.verts.new((X, Y, Z)))

        rings.append(ring)
    bm.verts.ensure_lookup_table()

    for i in range(segments):
        for j in range(4):
            v1 = rings[i][j]
            v2 = rings[i][(j + 1) % 4]
            v3 = rings[i + 1][(j + 1) % 4]
            v4 = rings[i + 1][j]
            bm.faces.new((v1, v2, v3, v4))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    if angle != 2 * np.pi:
        bm.faces.new((
            rings[0][0],
            rings[0][1],
            rings[0][2],
            rings[0][3],
        ))

        bm.faces.new((
            rings[-1][3],
            rings[-1][2],
            rings[-1][1],
            rings[-1][0],
        ))
    shade_smooth(bm)

    bm.to_mesh(mesh)
    bm.free()
    return create_object(name, mesh, mat)

def render_object(collection, parent, obj, rot = (0, 0, 0), loc = (0, 0, 0), scale = (1,1,1)):
    obj.parent = parent
    obj.rotation_euler = rot
    obj.location = loc
    obj.scale = scale
    collection.objects.link(obj)

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
    return text_obj

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

def get_donut_object_from_shape(shape, mat, r, mr, angle):
    if shape in {'circle'}:
        obj = create_partial_donat(mat, major_radius=r, minor_radius=mr, angle=angle)
    else:
        obj = create_cubic_partial_donut(mat, major_radius=r, half_size=mr, angle=angle)
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
    if cell_type == 'label': return val
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

def render_legend(target, props, data, mats, label_mat, label_size, transposed):
    loc = bpy.context.scene.cursor.location
    labels = [ row[0] for row in data ]
    space = label_size * 1.1

    #label_len = [ len(label) for label in labels ]
    loc = (loc[0] - space * (1+len(labels)), loc[1] + props.size[1], loc[2])
    #render_text_object(target["collection"], target["legend"], "Legend", loc, label_mat, size = space, x_align="LEFT", y_align="TOP")
    color_idx = 0
    for idx, label in enumerate(labels):
        if idx==0 and props.csv_format in {'header-left', 'header'} and not transposed: continue
        if idx==0 and props.csv_format in {'header-left', 'left'} and transposed: continue
        loc = (loc[0] + space, loc[1], loc[2])
        zoffset = - space / 4
        if props.chart_type in {'bar','column'}:
            obj = get_object_from_shape(props.bc_shape, mats[color_idx])
        elif props.chart_type in {'donut'}:
            zoffset = 0
            obj = get_donut_object_from_shape(props.donut_shape, mats[color_idx], 0.4, 0.2, 2*np.pi )
        else:
            obj = create_bar(mats[color_idx])

        render_object(target["collection"], target["legend"], obj, loc=( loc[0] + space/2, loc[1] + space/2, loc[2] + zoffset), scale=(space * .8 , space * .8, space/2.2))
        if (not transposed and props.csv_format in {'header-left', 'left'}) or (transposed and props.csv_format in {'header-left','header'}):
            text = label
        else:
            text = f"{color_idx+1}"
        render_text_object(target["collection"], target["legend"], text, (loc[0], loc[1] + space * 1.3, loc[2]), label_mat, size=space, x_align="LEFT", y_align="TOP")
        color_idx += 1

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

    xspace = props.size[0] / col_count
    yspace = props.size[1] / row_count

    label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)
    value_mat = create_material(props.value_color, roughness=props.value_roughness, metallic=props.value_metallic)
    minv = min(0, csv["minv"])
    zero_z_position = remap(0, minv, csv["maxv"], 0, props.size[2])
    if props.legend: render_legend(target, props, data, mats, label_mat, xspace/2, transposed)

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

    yspace = props.size[1] / row_count
    zspace = props.size[2] / col_count
    label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)
    value_mat = create_material(props.value_color, roughness=props.value_roughness, metallic=props.value_metallic)
    minv = min(0, csv["minv"])
    zero_x_position = remap(0, minv, csv["maxv"], 0, props.size[0])
    if props.legend: render_legend(target, props, data, mats, label_mat, zspace / 2, transposed)

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

    data = csv["rows"] if not transposed else list(map(list, zip(*csv["rows"])))
    mats = [create_material(get_color(i), roughness=props.roughness, metallic=props.metallic, alpha=props.alpha) for i in range(len(data))]
    sums = csv["row_sums"] if transposed else csv["col_sums"]
    abs_sums = csv["abs_row_sums"] if transposed else csv["abs_col_sums"]

    r1 = min(props.size[0]/20, props.size[2] /20)
    r = min(props.size[0]/2, props.size[2] /2)
    column_count = get_data_column_count(props, data, transposed)
    rs = -(r-r1) / column_count
    rsh = rs/2
    gap = min(props.spacing[0], props.spacing[2])
    last_radius = r

    if props.legend:
        label_mat = create_material(props.label_color, roughness=props.label_roughness, metallic=props.label_metallic)
        render_legend(target, props, data, mats, label_mat, props.size[1] / (2*column_count), transposed)

    loc = (cx + props.size[0] / 2, cy, cz + props.size[2] / 2)
    for row in range(len(data[0])):
        color_idx = 0
        if row == 0 and labels_left: continue
        last_angle = ph
        if abs_sums[row] != sums[row]:
            last_radius += rs
            continue
        for col in range(len(data)):
            if col == 0 and labels_header: continue
            val = get_value_from_data(data[col][row])
            perc = val / sums[row]
            angle = tp * perc
            obj = get_donut_object_from_shape(props.donut_shape, mats[color_idx], last_radius + rsh, abs(rsh) - gap, angle)
            render_object(target["collection"], target["chart"], obj, loc=loc, rot = (ph, -last_angle, 0))
            color_idx += 1
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
    if labels_header:
        max_label_len=max([len(s) for s in data[0]])
    for row_idx, row in enumerate(data):
        for col_idx, cell in enumerate(row):
            loc = (cx + xspace * col_idx, cy, cz + props.size[2] - zspace * row_idx)
            rot = [ph, 0, 0]
            val = cell
            x_align = 'CENTER'
            size = min(xspace, zspace) * 0.5
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
                size = min(xspace, zspace) * .8 / len(val)
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

def render_chart(props, csv):
    np.random.seed(0)
    target  = init_target_collection()
    if props.chart_type == "column":
        render_column_chart(target , props, csv)
    elif props.chart_type == "bar":
        render_bar_chart(target, props, csv)
    elif props.chart_type == "donut":
        render_donut_chart(target, props, csv)
    elif props.chart_type == 'table':
        render_table(target, props, csv)