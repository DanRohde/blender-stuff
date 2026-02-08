import bpy
import bmesh
import numpy as np
from mathutils import Vector
from .common import remap

def create_object(name, mesh, mat):
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    return obj

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
        polyline.points[i].co = (i * x_space, 0, remap(float(data[i]), minv, maxv, minz, maxz)-z_offset, 1)

    return create_object(name, curve_data, mat)


def create_area_chart(mat, data, bottom=None, thickness = 1, minv = 0, maxv = 1, minz = 0, maxz = 1, x_space = 1, z_offset = 0):
    name = "QuickChartAreaChart"
    point_count = len(data)
    if point_count<2:
        return None
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    xp = 0
    zv = float(data[0]) if bottom is None else float(bottom[0]) + float(data[0])
    z = remap(zv, minv, maxv, minz, maxz) - z_offset
    t1 = bm.verts.new((xp, 0, z))
    t4 = bm.verts.new((xp, thickness, z))

    zv = 0 if bottom is None else float(bottom[0])
    z = remap(zv, minv, maxv, minz, maxz) - z_offset
    b1 = bm.verts.new((xp, 0, z))
    b4 = bm.verts.new((xp, thickness, z))
    for idx in range(point_count-1):
        # top face:
        zv = float(data[idx+1]) if bottom is None else float(bottom[idx+1]) + float(data[idx+1])
        z = remap(zv, minv, maxv, minz, maxz) - z_offset
        t2 = bm.verts.new((xp + x_space, 0, z))
        t3 = bm.verts.new((xp + x_space, thickness, z))
        bm.faces.new((t1, t2, t3, t4))

        zv = 0 if bottom is None else float(bottom[idx+1])
        z = remap(zv, minv, maxv, minz, maxz) - z_offset
        b2 = bm.verts.new((xp + x_space, 0, z))
        b3 = bm.verts.new((xp + x_space, thickness, z))
        # bottom face:
        bm.faces.new((b1, b2, b3, b4))

        if idx == 0:
            # left face:
            bm.faces.new((t1, t4, b4, b1))
        if idx == point_count - 2:
            # right face:
            bm.faces.new((t2, t3, b3, b2))

        # front face:
        bm.faces.new((b1,b2,t2,t1))
        # back face:
        bm.faces.new((t3,t4,b4,b3))
        xp += x_space
        t1, t4 = t2, t3
        b1, b4 = b2, b3

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()
    return create_object(name, mesh, mat)

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

def create_area_light(target, name, location, target_loc, power=500, size=5, color=(1.0, 1.0, 1.0), spread=60):
    light_data = bpy.data.lights.new(name=name, type='AREA')
    light_data.energy = power
    light_data.size = size
    light_data.color = color
    light_data.spread = np.radians(spread)

    light_obj = bpy.data.objects.new(name, light_data)
    target["collection"].objects.link(light_obj)

    light_obj.location = location
    direction = Vector(target_loc) - light_obj.location
    light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    return light_obj

def create_camera(target, name, location, target_loc, ortho_scale=2):
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = ortho_scale
    cam_obj = bpy.data.objects.new(name, cam_data)
    target["collection"].objects.link(cam_obj)

    cam_obj.location = location
    direction = Vector(target_loc) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    bpy.context.scene.camera = cam_obj

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

def create_material(color, roughness = 0.5, metallic = 0, alpha = None):
    mat = bpy.data.materials.new("QuickChartMat1")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha if alpha is not None else color[3]
    return mat

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

def render_object(collection, parent, obj, rot = (0, 0, 0), loc = (0, 0, 0), scale = (1,1,1)):
    obj.parent = parent
    obj.rotation_euler = rot
    obj.location = loc
    obj.scale = scale
    collection.objects.link(obj)
