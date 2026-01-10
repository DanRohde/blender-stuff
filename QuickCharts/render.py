from MaterialX import createValueFromStrings

import bpy
import bmesh
import numpy as np

COLORS = [
    (0,1,1,1),
    (0,1,0,1),
    (0,0,1,1),
    (1,0,1,1),
    (1,1,0,1),
    (1,1,1,1),
]

def create_object(name, mesh, mat):
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    return obj

def clone_and_scale_object(target_collection, obj, scale, loc):
    new_obj = bpy.data.objects.new(name=obj.name, object_data=obj.data)
    new_obj.scale = scale
    new_obj.location = loc
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
    bmesh.ops.create_cone(bm, segments=64, radius1=.5, radius2=.5, depth=1, cap_ends=True)
    origin_to_bottom(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return create_object(name, mesh, mat)

def create_cone(mat):
    name = "QuickChartCone"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=64, radius1=.5, radius2=0, depth=1, cap_ends=True)
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

def create_material(color):
    mat = bpy.data.materials.new("QuickChartMat1")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
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

def get_object_from_shape(shape, color_idx):
    if color_idx > len(COLORS)-1:
        color = np.random.rand(4)
        color[3] = 1
    else:
        color = COLORS[color_idx]
    mat = create_material(color)
    if shape == 'cone': obj = create_cone(mat)
    elif shape == 'cylinder': obj = create_cylinder(mat)
    elif shape == 'pyramid': obj = create_pyramid(mat)
    else: obj = create_bar(mat)
    return obj

def remap(x, in_min, in_max, out_min, out_max):
    return out_min + ((x - in_min) / (in_max - in_min)) * (out_max - out_min)

def render_column_chart(target_collection, props, csv):
    chart_props = props.chart_properties
    csv_props = props.csv_properties
    lx, ly, lz = bpy.context.scene.cursor.location
    maxz = chart_props.size[2]/2
    z_max_v = max(abs(chart_props.min_xyz[2]), abs(chart_props.max_xyz[2]))

    transposed = chart_props.data_series == 'columns'

    data = csv if not transposed else list(map(list, zip(*csv))) # transpose csv if necessary

    xspace = chart_props.size[0] / len(csv[0])
    objects = [get_object_from_shape(chart_props.three_d_shape, i) for i in range(len(csv))]

    label_mat = create_material((1,1,1,1))

    if chart_props.bc_sub_type == 'normal': # checked with left, header, and header-left
        xs_space = xspace / len(data) - chart_props.spacing[0]
        for x in range(len(data[0])):
            if x == 0:
                if (not transposed and csv_props.csv_format in {'left', 'header-left'}) or (csv_props.csv_format in {'header','header-left'} and transposed):
                    continue  # skip label
            for xs in range(len(data)):
                if xs == 0:
                    if (not transposed and csv_props.csv_format in {'header','header-left'}) or (transposed and csv_props.csv_format in {'left','header-left'}):
                        render_text_object(target_collection, data[0][x], (lx + x * xspace + xspace/2, ly - xspace/2, lz + maxz), label_mat, size= xspace/2)
                        continue  # skip label
                loc = (lx + x * xspace + (xs-1) * xs_space, ly, lz + maxz)
                val = float(data[xs][x])
                valstr = f"{val:.1f}" # TODO: column type!
                zscale = remap(val, -z_max_v, z_max_v, -maxz, maxz)
                clone_and_scale_object(target_collection, objects[xs], (xs_space, xs_space, zscale), loc)
                render_text_object(target_collection, valstr, (loc[0], loc[1], lz + maxz + (zscale if val > 0 else 0)), label_mat, size = xs_space/2 * 3/len(valstr), x_align='CENTER', y_align='BOTTOM', rot=(np.pi/2,0,0) )
    elif chart_props.bc_sub_type == 'deep':
        yspace = chart_props.size[1] / len(csv[0])
        for x in range(len(csv[0])):
            for y in range(len(csv)):
                if x == 0:
                    if (not transposed and csv_props.csv_format in {'left', 'header-left'}) or (transposed and csv_props.csv_format in {'header','header-left'}):
                        render_text_object(target_collection, data[y][x], (lx + len(csv) * xspace, ly + y * yspace, lz + maxz), label_mat, rot=(0,0,0), x_align='LEFT', y_align='CENTER')
                        continue  # skip label
                if y == 0:
                    if (not transposed and csv_props.csv_format in {'header', 'header-left'}) or (transposed and csv_props.csv_format in {'header-left', 'left'}):
                        render_text_object(target_collection, data[0][x], (lx + x * xspace, ly, lz + maxz ), label_mat, y_align='CENTER')
                        continue # skip label
                loc = (lx + x * xspace, ly + y * yspace, lz + maxz)
                zscale = remap(float(data[y][x]), -z_max_v, z_max_v, -maxz, maxz)
                clone_and_scale_object(target_collection, objects[y], (xspace - chart_props.spacing[0]*2, yspace - chart_props.spacing[1]*2, zscale), loc)


def render_chart(props, csv):
    np.random.seed(0)
    target_collection = init_target_collection()
    if props.chart_properties.chart_type == "column":
        render_column_chart(target_collection, props, csv)
