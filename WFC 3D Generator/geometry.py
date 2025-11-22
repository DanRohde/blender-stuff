import bpy
from mathutils import Matrix
import math

def get_elements_on_side(obj, face='FRONT', threshold=0.001):
    bbox = obj.bound_box
    local_bbox = [Vector(b) for b in bbox]
    world_bbox = [obj.matrix_world @ v for v in local_bbox]
    
    min_x = min(v.x for v in world_bbox)
    max_x = max(v.x for v in world_bbox)
    min_y = min(v.y for v in world_bbox)
    max_y = max(v.y for v in world_bbox)
    min_z = min(v.z for v in world_bbox)
    max_z = max(v.z for v in world_bbox)
    
    if face == 'FRONT':
        threshold_value = max_z - threshold
        axis = 'z'
        direction = 'max'
    elif face == 'BACK':
        threshold_value = min_z + threshold
        axis = 'z'
        direction = 'min'
    elif face == 'RIGHT':
        threshold_value = max_x - threshold
        axis = 'x'
        direction = 'max'
    elif face == 'LEFT':
        threshold_value = min_x + threshold
        axis = 'x'
        direction = 'min'
    elif face == 'TOP':
        threshold_value = max_y - threshold
        axis = 'y'
        direction = 'max'
    elif face == 'BOTTOM':
        threshold_value = min_y + threshold
        axis = 'y'
        direction = 'min'
    else:
        return [], []
    
    relevant_edges = []
    for edge in obj.data.edges:
        vertices = [obj.data.vertices[i] for i in edge.vertices]
        world_vertices = [obj.matrix_world @ v.co for v in vertices]
        
        if direction == 'max':
            if all(getattr(v, axis) >= threshold_value for v in world_vertices):
                relevant_edges.append(edge)
        else:
            if all(getattr(v, axis) <= threshold_value for v in world_vertices):
                relevant_edges.append(edge)
    
    relevant_faces = []
    for poly in obj.data.polygons:
        vertices = [obj.data.vertices[i] for i in poly.vertices]
        world_vertices = [obj.matrix_world @ v.co for v in vertices]
        
        if direction == 'max':
            if all(getattr(v, axis) >= threshold_value for v in world_vertices):
                relevant_faces.append(poly)
        else:
            if all(getattr(v, axis) <= threshold_value for v in world_vertices):
                relevant_faces.append(poly)
    
    return relevant_edges, relevant_faces

def get_rotation_matrix(face):
    rotations = {
        'FRONT': Matrix.Identity(4),
        'BACK': Matrix.Rotation(math.pi, 4, 'Y'),
        'RIGHT': Matrix.Rotation(-math.pi/2, 4, 'Y'),
        'LEFT': Matrix.Rotation(math.pi/2, 4, 'Y'),
        'TOP': Matrix.Rotation(math.pi/2, 4, 'X'),
        'BOTTOM': Matrix.Rotation(-math.pi/2, 4, 'X')
    }
    return rotations.get(face, Matrix.Identity(4))

def normalize_geometry(obj, face, edges, faces):
    local_matrix = obj.matrix_world.inverted()
    rot_matrix = get_rotation_matrix(side)

    norm_edges = []
    for edge in edges:
        v1 = local_matrix @ obj.data.vertices[edge.vertices[0]].co
        v2 = local_matrix @ obj.data.vertices[edge.vertices[1]].co
        norm_edges.append((rot_matrix @ v1, rot_matrix @ v2))
    
    norm_faces = []
    for face in faces:
        vertices = [rot_matrix @ (local_matrix @ obj.data.vertices[i].co) 
                   for i in face.vertices]
        vertices = normalize_face_orientation(vertices)
        norm_faces.append(vertices)
    
    return norm_edges, norm_faces

def vectors_equal(v1, v2, tolerance=1e-6):
    return all(abs(a - b) < tolerance for a, b in zip(v1, v2))

def normalize_face_orientation(vertices):
    if len(vertices) < 3:
        return vertices
    
    v1 = vertices[1] - vertices[0]
    v2 = vertices[2] - vertices[0]
    normal = v1.cross(v2)
    
    if normal.z < 0:
        return vertices[::-1]
    return vertices

def remove_duplicate_edges(edges):
    unique_edges = []
    for edge in edges:
        sorted_edge = tuple(sorted(edge, key=lambda v: (v.x, v.y, v.z)))
        if sorted_edge not in unique_edges:
            unique_edges.append(sorted_edge)
    return unique_edges

def get_normalized_elements(obj, face):
    edges, faces = get_elements_on_side(obj, face)
    return normalize_geometry(obj, face, edges, faces)

def compare_sides(obj_a, face_a, obj_b, face_b, tolerance=1e-6):
    norm_edges_a, norm_faces_a = get_normalized_elements(obj_a, face_a)
    norm_edges_b, norm_faces_b = get_normalized_elements(obj_b, face_b)

    unique_edges_a = remove_duplicate_edges(norm_edges_a)
    unique_edges_b = remove_duplicate_edges(norm_edges_b)

    matching_edges = []
    for edge_a in unique_edges_a:
        for edge_b in unique_edges_b:
            if (vectors_equal(edge_a[0], edge_b[0], tolerance) and 
                vectors_equal(edge_a[1], edge_b[1], tolerance)) or \
               (vectors_equal(edge_a[0], edge_b[1], tolerance) and 
                vectors_equal(edge_a[1], edge_b[0], tolerance)):
                matching_edges.append(edge_a)
                break
    
    matching_faces = []
    for face_a in norm_faces_a:
        for face_b in norm_faces_b:
            if len(face_a) != len(face_b):
                continue
            match = True
            for vertex_a in face_a:
                found = False
                for vertex_b in face_b:
                    if vectors_equal(vertex_a, vertex_b, tolerance):
                        found = True
                        break
                if not found:
                    match = False
                    break
                    
            if match:
                matching_faces.append(face_a)
                break
    
    return {
        'obj_a_edges_count': len(unique_edges_a),
        'obj_b_edges_count': len(unique_edges_b),
        'matching_edges_count': len(matching_edges),
        'obj_a_faces_count': len(norm_faces_a),
        'obj_b_faces_count': len(norm_faces_b),
        'matching_faces_count': len(matching_faces)
    }
