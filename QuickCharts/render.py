import bpy
import bmesh
import numpy as np

from .constants import COLORS

def create_object(name, mesh, mat):
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    return obj

def clone_and_scale_object(target_collection, obj, scale, loc, rot = (0,0,0)):
    new_obj = bpy.data.objects.new(name=obj.name, object_data=obj.data)
    new_obj.scale = scale
    new_obj.location = loc
    new_obj.rotation_euler = rot
    new_obj.hide_viewport = False
    target_collection.objects.link(new_obj)
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

def create_cone(mat):
    name = "QuickChartCone"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=128, radius1=.5, radius2=0, depth=1, cap_ends=True)
    origin_to_bottom(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return create_object(name, mesh, mat)

def create_pyramid(mat):
    name = "QuickChartPyramid"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    half = .5
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

def create_material(color, roughness = 0.5, metallic = 0, alpha = 1):
    mat = bpy.data.materials.new("QuickChartMat1")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    return mat

def render_text_object(target_collection, text, loc, mat, rot = (0, 0, np.pi / 2), x_align = 'RIGHT', y_align = 'BOTTOM', size = 1):
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
    target_collection.objects.link(text_obj)
    text_obj.data.materials.append(mat)

def init_target_collection():
    target_collection = bpy.data.collections.new("QuickChartCollection")
    bpy.context.scene.collection.children.link(target_collection)
    return target_collection

def get_object_from_shape(shape, color_idx, roughness = 0.5, metallic = 0, alpha = 1):
    if color_idx > len(COLORS)-1:
        color = np.random.rand(4)
        color[3] = 1
    else:
        color = COLORS[color_idx]
    mat = create_material(color, roughness=roughness, metallic=metallic, alpha=alpha)
    if shape == 'cone': obj = create_cone(mat)
    elif shape == 'cylinder': obj = create_cylinder(mat)
    elif shape == 'pyramid': obj = create_pyramid(mat)
    else: obj = create_bar(mat)
    return obj

def remap(x, in_min, in_max, out_min, out_max):
    return out_min + ((x - in_min) / (in_max - in_min)) * (out_max - out_min)

def render_column_chart(target_collection, props, csv):
    lx, ly, lz = bpy.context.scene.cursor.location
    maxz = props.size[2]/2
    z_max_v = max(abs(props.min_xyz[2]), abs(props.max_xyz[2]))

    transposed = props.data_series == 'columns'

    data = csv if not transposed else list(map(list, zip(*csv))) # transpose csv if necessary

    xspace = props.size[0] / len(data[0])
    objects = [get_object_from_shape(props.bc_shape, i, roughness=props.roughness, metallic=props.metallic, alpha=props.alpha) for i in range(len(csv))]

    label_mat = create_material((1,1,1,1), roughness=props.roughness, metallic=props.metallic)

    if props.bc_sub_type == 'normal': # checked with left, header, and header-left
        xs_space = xspace / len(data) - props.spacing[0]
        for x in range(len(data[0])):
            if x == 0:
                if (not transposed and props.csv_format in {'left', 'header-left'}) or (props.csv_format in {'header','header-left'} and transposed):
                    continue  # skip label
            color_idx = 0
            for xs in range(len(data)):
                if xs == 0:
                    if (not transposed and props.csv_format in {'header','header-left'}) or (transposed and props.csv_format in {'left','header-left'}):
                        if props.labels: render_text_object(target_collection, data[0][x], (lx + x * xspace + xspace/2, ly - xspace/2, lz + maxz), label_mat, size= xspace/2)
                        continue  # skip label
                loc = (lx + x * xspace + (xs-1) * xs_space, ly, lz + maxz)
                try:
                    val = float(data[xs][x])
                except ValueError:
                    val = 0.0
                valstr = f"{val:.1f}" # TODO: column type!
                zscale = remap(val, -z_max_v, z_max_v, -maxz, maxz)
                clone_and_scale_object(target_collection, objects[color_idx], (xs_space, xs_space, zscale), loc)
                color_idx += 1
                if props.values: render_text_object(target_collection, valstr, (loc[0], loc[1], lz + maxz + (zscale if val > 0 else 0)), label_mat, size = xs_space/2 * 3/len(valstr), x_align='CENTER', y_align='BOTTOM', rot=(np.pi/2,0,0) )
    elif props.bc_sub_type == 'deep':
        yspace = props.size[1] / len(data[0])
        for x in range(len(data[0])):
            color_idx = 0
            for y in range(len(data)):
                if x == 0:
                    if (not transposed and props.csv_format in {'left', 'header-left'}) or (transposed and props.csv_format in {'header','header-left'}):
                        if props.labels: render_text_object(target_collection, data[y][x], (lx + len(data[0]) * xspace, ly + y * yspace, lz + maxz), label_mat, rot=(0,0,0), x_align='LEFT', y_align='CENTER')
                        continue  # skip label
                if y == 0:
                    if (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'header-left', 'left'}):
                        if props.labels: render_text_object(target_collection, data[0][x], (lx + x * xspace, ly, lz + maxz ), label_mat, y_align='CENTER')
                        continue # skip label
                loc = (lx + x * xspace, ly + y * yspace, lz + maxz)
                try:
                    val = float(data[y][x])
                except ValueError:
                    val = 0.0
                valstr = f"{val:.1f}"  # TODO: column type!
                zscale = remap(val, -z_max_v, z_max_v, -maxz, maxz)
                clone_and_scale_object(target_collection, objects[color_idx], (xspace - props.spacing[0]*2, yspace - props.spacing[1]*2, zscale), loc)
                color_idx += 1
                if props.values: render_text_object(target_collection, valstr, (loc[0], loc[1], lz + maxz + (zscale if val > 0 else 0)), label_mat, size = xspace/2 * 2/len(valstr), x_align='CENTER', y_align='BOTTOM', rot=(np.pi/2,0,0) )

def render_bar_chart(target_collection, props, csv):
    lx, ly, lz = bpy.context.scene.cursor.location
    maxx = props.size[0] / 2
    x_max_v = max(abs(props.min_xyz[2]), abs(props.max_xyz[2]))
    ph = np.pi / 2

    transposed = props.data_series == 'columns'
    data = csv if not transposed else list(map(list, zip(*csv)))  # transpose csv if necessary

    zspace = props.size[2] / len(data[0])
    objects = [get_object_from_shape(props.bc_shape, i, roughness=props.roughness, metallic=props.metallic, alpha=props.alpha) for i in range(len(csv))]

    label_mat = create_material((1, 1, 1, 1), roughness=props.roughness, metallic=props.metallic)

    if props.bc_sub_type == 'normal':
        zs_space = zspace / len(data) - props.spacing[0]
        for z in range(len(data[0])):
            if z == 0:
                if (not transposed and props.csv_format in {'left', 'header-left'}) or (props.csv_format in {'header', 'header-left'} and transposed):
                    continue  # skip label
            color_idx = 0
            for zs in range(len(data)):
                if zs == 0:
                    if (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'left', 'header-left'}):
                        if props.labels: render_text_object(target_collection, data[0][z], (lx + maxx , ly - zspace / 2, lz + z * zspace + zspace / 2), label_mat, size=zspace / 2, rot=(ph,0,ph), x_align='RIGHT', y_align='TOP')
                        continue  # skip label
                loc = (lx + maxx, ly, lz + z * zspace + (zs - 1) * zs_space)
                try:
                    val = float(data[zs][z])
                except ValueError:
                    val = 0.0
                valstr = f"{val:.1f}"  # TODO: column type!
                xscale = remap(val, -x_max_v, x_max_v, -maxx, maxx)
                clone_and_scale_object(target_collection, objects[color_idx], (zs_space, zs_space, xscale), loc, rot=(0, ph, 0))
                color_idx += 1
                if props.values: render_text_object(target_collection, valstr, (lx + maxx + (xscale if val > 0 else 0), loc[1], loc[2]), label_mat, size=zs_space / 2 * 3 / len(valstr), x_align='LEFT', y_align='CENTER', rot=(np.pi / 2, 0, 0))
    elif props.bc_sub_type == 'deep':
        yspace = props.size[1] / len(data[0])
        for z in range(len(data[0])):
            color_idx = 0
            for y in range(len(data)):
                if z == 0:
                    if (not transposed and props.csv_format in {'left', 'header-left'}) or (transposed and props.csv_format in {'header', 'header-left'}):
                        if props.labels: render_text_object(target_collection, data[y][z], (lx + maxx , ly + y * yspace, lz + len(data[0]) * zspace), label_mat, rot=(ph, 0, ph), x_align='RIGHT' if y==0 else 'CENTER', y_align='CENTER')
                        continue  # skip label
                if y == 0:
                    if (not transposed and props.csv_format in {'header', 'header-left'}) or (transposed and props.csv_format in {'header-left', 'left'}):
                        if props.labels: render_text_object(target_collection, data[0][z], (lx + maxx , ly, lz + z * zspace ), label_mat, x_align='RIGHT', y_align='CENTER', rot=(ph, 0, ph))
                        continue  # skip label
                loc = (lx + maxx , ly + y * yspace, lz + z * zspace )
                try:
                    val = float(data[y][z])
                except ValueError:
                    val = 0.0
                valstr = f"{val:.1f}"  # TODO: column type!
                xscale = remap(val, -x_max_v, x_max_v, -maxx, maxx)
                clone_and_scale_object(target_collection, objects[color_idx], (zspace - props.spacing[2] * 2, yspace - props.spacing[1] * 2, xscale ), loc, rot=(0, np.pi/2, 0))
                color_idx += 1
                if props.values: render_text_object(target_collection, valstr, (lx + maxx + (xscale if val > 0 else 0), loc[1], loc[2]) , label_mat, size=zspace / 2 * 2 / len(valstr), x_align='LEFT', y_align='CENTER', rot=(np.pi / 2, 0, 0))


def render_chart(props, csv):
    np.random.seed(0)
    target_collection = init_target_collection()
    if props.chart_type == "column":
        render_column_chart(target_collection, props, csv)
    elif props.chart_type == "bar":
        render_bar_chart(target_collection, props, csv)