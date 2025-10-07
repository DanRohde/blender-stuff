# Written 2025 by Dan Rohde
# To make this add-on installable, create an extension with it:
# https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html

import bpy
import bmesh
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy.props import IntProperty
from bpy.props import BoolProperty

import math
from mathutils import Vector


def create_sierpinski_triangle(level, size):
    def subdivide_triangle(vertices, level):
        if level == 0:
            return [vertices]

        midpoints = [
            ((vertices[0][0] + vertices[1][0]) / 2, (vertices[0][1] + vertices[1][1]) / 2, (vertices[0][2] + vertices[1][2]) / 2),
            ((vertices[1][0] + vertices[2][0]) / 2, (vertices[1][1] + vertices[2][1]) / 2, (vertices[1][2] + vertices[2][2]) / 2),
            ((vertices[2][0] + vertices[0][0]) / 2, (vertices[2][1] + vertices[0][1]) / 2, (vertices[2][2] + vertices[0][2]) / 2)
        ]

        triangles = [
            [vertices[0], midpoints[0], midpoints[2]],
            [vertices[1], midpoints[1], midpoints[0]],
            [vertices[2], midpoints[2], midpoints[1]]
        ]

        result = []
        for triangle in triangles:
            result.extend(subdivide_triangle(triangle, level - 1))

        return result

    vertices = [
        (-size / 2, -size / 2 * math.sqrt(3) / 3, 0),
        (size / 2, -size / 2 * math.sqrt(3) / 3, 0),
        (0, size / 2 * math.sqrt(3) / 3 * 2, 0)
    ]

    triangles = subdivide_triangle(vertices, level)

    mesh = bpy.data.meshes.new("SierpinskiTriangle")
    bm = bmesh.new()

    for triangle in triangles:
        verts = [bm.verts.new(v) for v in triangle]
        bm.faces.new(verts)

    bm.to_mesh(mesh)
    mesh.update()

    obj = bpy.data.objects.new("SierpinskiTriangle", mesh)
    bpy.context.collection.objects.link(obj)


class OBJECT_OT_add_sierpinski_triangle(Operator):
    bl_idname = "object.sierpinski_triangle"
    bl_label = "Generate Sierpinski Triangle"
    bl_options = {'REGISTER', 'UNDO'}

    level: bpy.props.IntProperty(name="Level", default=3, min=0, max=10)
    size: bpy.props.FloatProperty(name="Size", default=2.0, min=0.1, max=10.0)

    def execute(self, context):
        create_sierpinski_triangle(self.level, self.size)
        return {'FINISHED'}


def move_vert_to_location(vert,l):
    v=list(vert)
    return (v[0]+l[0],v[1]+l[1],v[2]+l[2])

def get_obj_size(obj):
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    min_x = min(v.x for v in bbox_corners)
    max_x = max(v.x for v in bbox_corners)
    min_y = min(v.y for v in bbox_corners)
    max_y = max(v.y for v in bbox_corners)
    min_z = min(v.z for v in bbox_corners)
    max_z = max(v.z for v in bbox_corners)
    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z
    return (size_x, size_y, size_z)
    
def clone_obj(obj, orig_data, location):
    mesh_copy = orig_data.copy()
    obj_copy = obj.copy()
    obj_copy.data = mesh_copy
    obj_copy.location = location
    bpy.context.collection.objects.link(obj_copy)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj_copy.select_set(True)
    bpy.ops.object.join()
    return obj
            
def create_pyramid(mesh, location, size):
    hs=size/2
    vertices = [ (hs,hs,0), (hs,-hs,0), (-hs,-hs,0), (-hs,hs,0), (0,0,size) ]
    bm = bmesh.new()
    bm.from_mesh(mesh)
    o = len(bm.verts)
    for v in vertices:
        bm.verts.new(move_vert_to_location(v,location))
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.faces.new([bm.verts[0+o],bm.verts[1+o],bm.verts[2+o],bm.verts[3+o]])
    bm.faces.new([bm.verts[0+o],bm.verts[1+o],bm.verts[4+o]])
    bm.faces.new([bm.verts[1+o],bm.verts[2+o],bm.verts[4+o]])
    bm.faces.new([bm.verts[2+o],bm.verts[3+o],bm.verts[4+o]])
    bm.faces.new([bm.verts[3+o],bm.verts[0+o],bm.verts[4+o]])
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
    return mesh


def mult_dist_factor(f,t):
    newlist=[f*i for i in t]
    return tuple(newlist)

def create_sierpinski_pyramid(self):
    orig_obj = bpy.context.active_object
    if self.useselection and orig_obj and orig_obj.type == 'MESH':
        mesh = orig_obj.data.copy()
        orig_data = orig_obj.data  
    else:
        mesh = bpy.data.meshes.new("Sierpinski Pyramid")
        create_pyramid(mesh, Vector((0, 0, 0)), self.size)
        orig_data=mesh.copy()
        
    # deselect all
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    
    obj = bpy.data.objects.new("Sierpinski Pyramid", mesh)
    bpy.context.collection.objects.link(obj)

    obj_size = get_obj_size(obj)
    for i in range(self.iterations):
        hx=obj_size[0]/2
        hy=obj_size[1]/2
        obj.location=mult_dist_factor(self.distfactor,(0,0,obj_size[2]))
        clone_obj(obj,orig_data,mult_dist_factor(self.distfactor,(-hx, hy, 0)))
        clone_obj(obj,orig_data,mult_dist_factor(self.distfactor,(hx,hy,0)))
        clone_obj(obj,orig_data,mult_dist_factor(self.distfactor,(-hx,-hy,0)))
        clone_obj(obj,orig_data,mult_dist_factor(self.distfactor,(hx,-hy,0)))
        
        obj_size=tuple([2*i for i in obj_size])
        orig_data = obj.data.copy()
    return obj

class OBJECT_OT_add_sierpinski_pyramid(bpy.types.Operator):
    """Add a Sierpinski Pyramid"""
    bl_idname = "mesh.add_sierpinski_pyramid"
    bl_label = "Add Sierpinski Pyramid"
    bl_options = {'REGISTER', 'UNDO'}

   
    iterations: bpy.props.IntProperty(
        name="Iterations",
        description="Number of iterations for the Sierpinski Pyramid",
        default=2,
        min=0,
        max=5,
    )
    size: bpy.props.FloatProperty(
        name="Pyramid Size",
        description="Size of the Sierpinski Pyramid",
        default=2.0,
        min=0.1,
        max=10.0,
    )
    distfactor: bpy.props.FloatProperty(
        name="Distance factor",
        description="Adjust the distance between base objects",
        default=1.0,
    )
    useselection: bpy.props.BoolProperty(
        name="Use selection",
        description="Use selection to create a Sierpinski pyramid",
        default=True,
    ) 
    def execute(self, context):
        create_sierpinski_pyramid(self)
        return {'FINISHED'}


# Registration

def add_triangle_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_sierpinski_triangle.bl_idname,
        text="Sierpinski Triangle",
        icon='PLUGIN',
    )
def add_pyramid_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_sierpinski_pyramid.bl_idname,
        text="Sierpinski Pyramid",
        icon='PLUGIN',
    )


# This allows you to right click on a button and link to documentation
#def add_object_manual_map():
#    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
#    url_manual_mapping = (
#        ("bpy.ops.mesh.add_object", "scene_layout/object/types.html"),
#    )
#    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_sierpinski_triangle)
    bpy.utils.register_class(OBJECT_OT_add_sierpinski_pyramid)
    bpy.types.VIEW3D_MT_mesh_add.append(add_triangle_button)
    bpy.types.VIEW3D_MT_mesh_add.append(add_pyramid_button)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_sierpinski_triangle)
    bpy.utils.unregister_class(OBJECT_OT_add_sierpinski_pyramid)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_triangle_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_pyramid_button)


if __name__ == "__main__":
    register()
