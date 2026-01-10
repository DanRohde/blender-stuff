import bpy
import bmesh
from mathutils import Matrix
import math

def create_object(target_collection, name, loc, mesh, mat):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.data.materials.append(mat)
    target_collection.objects.link(obj)

def origin_to_bottom(bm):
    min_z = min(v.co.z for v in bm.verts)

    for v in bm.verts:
        v.co.z -= min_z

def render_bar(target_collection, loc, width, height, mat):
    name = "QuickChartBar"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=.5)
    bmesh.ops.scale(bm, vec=(width, height, 1), verts = bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=bm.verts )
    origin_to_bottom(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    create_object(target_collection, name, loc, mesh, mat)

def render_3d_bar(target_collection, loc, width, depth, height, mat):
    name = "QuickChart3DBar"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size = 1 )
    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)
    origin_to_bottom(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    create_object(target_collection, name, loc, mesh, mat)

def render_cylinder(target_collection, loc, radius, height, mat):
    name = "QuickChartCylinder"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=32, radius1=1, radius2=1, depth=1, cap_ends=True)
    bmesh.ops.scale(bm, vec=(radius, radius, height), verts=bm.verts)
    origin_to_bottom(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    create_object(target_collection, name, loc, mesh, mat)

def render_cone(target_collection, loc, radius, height, mat):
    name = "QuickChartCone"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=32, radius1=1, radius2=0, depth=1, cap_ends=True)
    bmesh.ops.scale(bm, vec=(radius, radius, height), verts=bm.verts)
    origin_to_bottom(bm)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    create_object(target_collection, name, loc, mesh, mat)

def render_pyramid(target_collection, loc, size, height, mat):
    name = "QuickChartPyramid"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    half = size / 2
    v0 = bm.verts.new((-half, -half, 0))
    v1 = bm.verts.new(( half, -half, 0))
    v2 = bm.verts.new(( half,  half, 0))
    v3 = bm.verts.new((-half,  half, 0))
    top = bm.verts.new((0, 0, height))

    bm.faces.new((v0, v1, v2, v3))
    bm.faces.new((v0, v1, top))
    bm.faces.new((v1, v2, top))
    bm.faces.new((v2, v3, top))
    bm.faces.new((v3, v0, top))

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    create_object(target_collection, name, loc, mesh, mat)

def create_material(color):
    mat = bpy.data.materials.new("QuickChartMat1")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    return mat

def render_chart(props, csv):
    mat = create_material((1, 0, 0, 1))
    target_collection = bpy.data.collections.new("QuickChartCollection")
    bpy.context.scene.collection.children.link(target_collection)
    render_bar(target_collection,(0,0,0), 1, 1, mat )
    render_3d_bar(target_collection,(2,0,0), 1, 1, 2, mat )
    render_cone(target_collection, (4,0,0), .5, 3, mat)
    render_cylinder(target_collection, (6, 0, 0), .5, 4, mat)
    render_pyramid(target_collection, (8,0,0), 1, 5, mat)