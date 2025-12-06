from mathutils import Matrix, Vector
import math
from .helper import get_default_empty_name, get_default_empty_object

def get_bounding_box(obj, spacing):
    local_bbox = [Vector(v) for v in obj.bound_box]

    min_x = min(min(v.x for v in local_bbox), -spacing[0]/2)
    max_x = max(max(v.x for v in local_bbox), spacing[0]/2)
    min_y = min(min(v.y for v in local_bbox), -spacing[1]/2)
    max_y = max(max(v.y for v in local_bbox), spacing[1]/2)
    min_z = min(min(v.z for v in local_bbox), -spacing[2]/2)
    max_z = max(max(v.z for v in local_bbox), spacing[2]/2)

    return min_x, max_x, min_y, max_y, min_z, max_z

def get_axis_direction(bbox, face, threshold):
    min_x, max_x, min_y, max_y, min_z, max_z = bbox
    if face == 'FRONT':
        threshold_value = min_y + threshold
        axis = 'y'
        direction = 'min'
    elif face == 'BACK':
        threshold_value = max_y - threshold
        axis = 'y'
        direction = 'max'
    elif face == 'RIGHT':
        threshold_value = max_x - threshold
        axis = 'x'
        direction = 'max'
    elif face == 'LEFT':
        threshold_value = min_x + threshold
        axis = 'x'
        direction = 'min'
    elif face == 'TOP':
        threshold_value = max_z - threshold
        axis = 'z'
        direction = 'max'
    elif face == 'BOTTOM':
        threshold_value = min_z + threshold
        axis = 'z'
        direction = 'min'
    else:
        return None
    return threshold_value, axis, direction

def get_elements_on_side(obj, data, face, spacing, threshold):
    threshold_value, axis, direction = get_axis_direction(get_bounding_box(obj, spacing), face, threshold)

    relevant_elements = []
    for element in data:
        vertices = [obj.data.vertices[i] for i in element.vertices]
        if direction == 'max':
            if all(getattr(v.co, axis) >= threshold_value for v in vertices):
                relevant_elements.append(element)
        else:
            if all(getattr(v.co, axis) <= threshold_value for v in vertices):
                relevant_elements.append(element)

    return relevant_elements


def get_edges_on_side(obj, face, spacing, threshold):
    return get_elements_on_side(obj, obj.data.edges, face, spacing, threshold)

def get_faces_on_side(obj, face, spacing, threshold):
    return get_elements_on_side(obj, obj.data.polygons, face, spacing, threshold)

def get_rotation_matrix(face):
    nd = math.pi / 2
    rotations = {
        'BACK': { 'angle': math.pi, 'axis': 'X' },
        'RIGHT': { 'angle': -nd, 'axis': 'Z' },
        'LEFT': { 'angle' : nd, 'axis': 'Z' },
        'TOP': { 'angle': nd, 'axis': 'X'},
        'BOTTOM': { 'angle': -nd, 'axis': 'X'},
    }
    if face == 'FRONT':
        return Matrix.Identity(3)
    else:
        return Matrix.Rotation(rotations[face]['angle'], 3, rotations[face]['axis'])

def normalize_edge_geometry(obj, face, edges):
    rot_matrix = get_rotation_matrix(face)

    norm_edges = []
    for edge in edges:
        v1 = obj.data.vertices[edge.vertices[0]].co
        v2 = obj.data.vertices[edge.vertices[1]].co
        norm_edges.append((rot_matrix @ v1, rot_matrix @ v2))
    
    return norm_edges

def normalize_face_geometry(obj, face, faces):
    rot_matrix = get_rotation_matrix(face)

    norm_faces = []
    for f in faces:
        vertices = [rot_matrix @ obj.data.vertices[i].co for i in f.vertices]
        vertices = normalize_face_orientation(vertices)
        norm_faces.append(vertices)
    
    return norm_faces

def vectors_equal(v1, v2, tolerance=1e-6):
    return all(abs(a - b) < tolerance for a, b in zip(v1, v2))

def normalize_face_orientation(vertices):
    if len(vertices) < 3: return vertices
    
    v1 = vertices[1] - vertices[0]
    v2 = vertices[2] - vertices[0]
    normal = v1.cross(v2)
    
    return vertices[::-1] if normal.y > 0 else vertices

def remove_duplicate_edges(edges):
    unique_edges = []
    for edge in edges:
        sorted_edge = tuple(sorted(edge, key=lambda v: (v.x, v.y, v.z)))
        if sorted_edge not in unique_edges:
            unique_edges.append(sorted_edge)
    return unique_edges

def get_normalized_edges(obj, face, spacing, threshold):
    return normalize_edge_geometry(obj, face, get_edges_on_side(obj, face, spacing, threshold))

def get_normalized_faces(obj, face, spacing, threshold):
    return normalize_face_geometry(obj, face, get_faces_on_side(obj, face, spacing, threshold))

def compare_edges(obj_a, face_a, obj_b, face_b, tolerance, threshold, spacing):
    unique_edges_a = remove_duplicate_edges(get_normalized_edges(obj_a, face_a, spacing, threshold))
    unique_edges_b = remove_duplicate_edges(get_normalized_edges(obj_b, face_b, spacing, threshold))
    matching_edge_count = 0
    for edge_a in unique_edges_a:
        for edge_b in unique_edges_b:
            if (vectors_equal(edge_a[0], edge_b[0], tolerance) and
                vectors_equal(edge_a[1], edge_b[1], tolerance)) or \
               (vectors_equal(edge_a[0], edge_b[1], tolerance) and
                vectors_equal(edge_a[1], edge_b[0], tolerance)):
                matching_edge_count += 1
                break
    return {
        'obj_a_edges_count': len(unique_edges_a),
        'obj_b_edges_count': len(unique_edges_b),
        'matching_edges_count': matching_edge_count,
    }


def compare_faces(obj_a, face_a, obj_b, face_b, tolerance, threshold, spacing):
    norm_faces_a = get_normalized_faces(obj_a, face_a, spacing, threshold)
    norm_faces_b = get_normalized_faces(obj_b, face_b, spacing, threshold)

    matching_face_count = 0
    for face_a in norm_faces_a:
        for face_b in norm_faces_b:
            if len(face_a) != len(face_b): continue
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
                matching_face_count =+ 1
                break
    
    return {
        'obj_a_faces_count': len(norm_faces_a),
        'obj_b_faces_count': len(norm_faces_b),
        'matching_faces_count': matching_face_count
    }
def get_bb(obj):
    local_bbox = [Vector(v) for v in obj.bound_box]

    min_x = min(v.x for v in local_bbox)
    max_x = max(v.x for v in local_bbox)
    min_y = min(v.y for v in local_bbox)
    max_y = max(v.y for v in local_bbox)
    min_z = min(v.z for v in local_bbox)
    max_z = max(v.z for v in local_bbox)

    return [ min_x, max_x, min_y, max_y, min_z, max_z ]

def get_max_size(max_size, obj, default_obj, prop_obj):
    bb = get_bb(obj)
    dimensions = default_obj["wfc_dim_xyz"] if default_obj is not None and "wfc_dim_xyz" in default_obj else (1, 1, 1)
    dimensions = prop_obj["wfc_dim_xyz"] if "wfc_dim_xyz" in prop_obj else dimensions
    obj_size = [(bb[1] - bb[0]) / dimensions[0], (bb[3] - bb[2]) / dimensions[1], (bb[5] - bb[4]) / dimensions[2]]
    if obj_size[0] > max_size[0]: max_size[0] = obj_size[0]
    if obj_size[1] > max_size[1]: max_size[1] = obj_size[1]
    if obj_size[2] > max_size[2]: max_size[2] = obj_size[2]
    return max_size
def auto_detect_spacing(props):
    max_size = [ 0, 0, 0 ]
    default_obj = get_default_empty_object(props.collection_obj, False)
    for obj in props.collection_obj.objects:
        if obj.name.startswith(get_default_empty_name()) or not hasattr(obj, "bound_box"): continue
        max_size = get_max_size(max_size, obj, default_obj, obj)
    for child in props.collection_obj.children:
        collection_default = get_default_empty_object(child, False)
        for obj in child.objects:
            if obj.name.startswith(get_default_empty_name()) or not hasattr(obj, "bound_box"): continue
            max_size = get_max_size(max_size, obj, default_obj, collection_default)
    return max_size