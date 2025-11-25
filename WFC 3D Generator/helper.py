from typing import Any
import bpy
from mathutils import noise, Vector
from .constants import *
from .vis import is_directions_geometry_nodegroup_visible


def get_icon_name(item):
    return ICON_MAP[item.obj.type] if item.obj.id_type != 'COLLECTION' else ICON_MAP[item.obj.id_type]

def get_default_empty_object(collection, create = False) -> Any | None:
    if get_default_empty_name() in collection.objects:
        return collection.objects[get_default_empty_name()]
    else:
        for o in collection.objects:
            if o.name.startswith(get_default_empty_name()):
                return o
        if not create: return None
        obj = bpy.data.objects.new(get_default_empty_name(), None)
        collection.objects.link(obj)
        obj.empty_display_type = 'SPHERE'
        obj.location = (0, 0, 0)
        obj.hide_viewport = True
        obj.hide_render = True
        return obj

def get_object_by_name(props, name):
    collection = props.collection_obj
    if props.edit_type == 'objects':
        if name in collection.objects:
            return collection.objects[name]
        elif name in collection.children:
            return get_default_empty_object(collection.children[name], True)
    elif props.edit_type == 'defaults':
        return get_default_empty_object(collection, True)
    return None

def get_constraints(props):
    constraints = []
    if props.edit_constraints == 'symmetry':
        constraints = SYMMETRY_CONSTRAINTS
    elif props.edit_constraints == 'frequency':
        constraints = FREQUENCY_CONSTRAINTS
    elif props.edit_constraints == 'transformation':
        constraints = TRANSFORMATION_CONSTRAINTS
    elif props.edit_constraints == 'probability':
        constraints = PROBABILITY_CONSTRAINTS
    elif props.edit_constraints == 'region':
        constraints = REGION_CONSTRAINTS
    elif props.edit_constraints == 'grid':
        constraints = GRID_CONSTRAINTS
    elif props.edit_constraints == 'neighbor':
        constraints = [props.edit_neighbor_constraint] + ADD_NEIGHBOR_CONSTRAINTS
    elif props.edit_constraints == 'connector':
        constraints = CONNECTOR_CONSTRAINTS
    elif props.edit_constraints == 'dimensions':
        constraints = DIMENSIONS_CONSTRAINTS
    elif props.edit_constraints == 'fixed_position':
        constraints = FIXED_POSITION_CONSTRAINTS
    elif props.edit_constraints == 'regfreq':
        constraints = REGFREQ_CONSTRAINTS
    elif props.edit_constraints == 'noise':
        constraints = NOISE_CONSTRAINTS
    elif props.edit_constraints == 'geometry':
        constraints = GEOMETRY_CONSTRAINTS
    elif props.edit_constraints == 'regprob':
        constraints = REGPROB_CONSTRAINTS
    elif props.edit_constraints == 'distance':
        constraints = DISTANCE_CONSTRAINTS
    return constraints

def get_selected_items(obj_list):
    return [item.obj.name for item in obj_list if item.obj is not None and item.selected]

def count_selected_items(obj_list):
    return len([item for item in obj_list if item.selected])

def update_constraints(props, constraints):
    items = []
    if props.edit_type == 'objects':
        items = get_selected_items(props.obj_list)
    elif props.edit_type == 'defaults':
        items = [get_default_empty_name()]

    default_object = get_default_empty_object(props.collection_obj, False)
    for item in items:
        obj = get_object_by_name(props, item)

        for c in constraints:
            prop_name = 'wfc_' + c
            if c in LIST_CONSTRAINTS:
                lc = LIST_CONSTRAINTS[c]
                idx = len(props.get(lc,[]))
                while f"{prop_name}_{idx}" in obj:
                    del obj[f"{prop_name}_{idx}"]
                    idx+=1
                for idx, li in enumerate(props.get(lc, [])):
                    obj[f"{prop_name}_{idx}"] = li.get(c, PROP_DEFAULTS[c])
            elif c in props:
                if not cmpall(props[c], PROP_DEFAULTS[c]) or (default_object and default_object != obj and prop_name in default_object and default_object[prop_name] != props[c]):
                    obj[prop_name] = props[c]
                elif prop_name in obj:
                    del obj[prop_name]

def update_connector_constraints(props):
    prop_name = props.conn_directions
    connector = props.conn_name
    if prop_name == '_NONE_': return
    if props.edit_type == 'objects':
        for item in get_selected_items(props.obj_list):
            obj = get_object_by_name(props, item)
            obj[prop_name] = connector
    elif props.edit_type == 'defaults':
        obj = get_object_by_name(props, get_default_empty_name())
        obj[prop_name] = connector

def update_grid_constraints(props):
    def _get_new_prop_val(props, prop_name, values):
        newval = []
        if prop_name + "_none" in props and props[prop_name + "_none"]:
            newval.append("-")
        else:
            for v in values:
                if '_' in v: v = v.split('_',1)[1]
                pn = prop_name + '_' + v.lower()
                if pn in props and props[pn]: newval.append(v.lower())
        return ",".join(newval)

    def _set_grid_constraints(obj, props):
        obj["wfc_corners"] = _get_new_prop_val(props, "corner", CORNER_DIRECTIONS)
        obj["wfc_edges"] = _get_new_prop_val(props, "edge", EDGE_DIRECTIONS)
        obj["wfc_faces"] = _get_new_prop_val(props, "face", FACE_DIRECTIONS)
        if props["inside_none"]:
            obj["wfc_inside"] = "-"
        else:
            obj["wfc_inside"] = ""

    if props.edit_type == 'objects':
        for item in get_selected_items(props.obj_list):
            _set_grid_constraints(get_object_by_name(props, item), props)
    elif props.edit_type == 'defaults':
        _set_grid_constraints(get_object_by_name(props, get_default_empty_name()), props)

def update_neighbor_constraints(props):
    def _set_neighbors(obj, prop_name, neighbors):
        obj[prop_name] = ",".join(neighbors)

    prop_name = props.edit_neighbor_constraint
    if props.no_neighbor_allowed:
        neighbors = ["-"]
    else:
        neighbors = get_selected_items(props.neighbor_list)
    if props.edit_type == 'objects':
        for item in get_selected_items(props.obj_list):
            obj = get_object_by_name(props, item)
            _set_neighbors(obj, prop_name, neighbors)
    elif props.edit_type == 'defaults':
        obj = get_object_by_name(props, get_default_empty_name())
        _set_neighbors(obj, prop_name, neighbors)
    update_constraints(props, ADD_NEIGHBOR_CONSTRAINTS)


def auto_save(_self, context):
    props = context.scene.wfc_props
    if not props.auto_save: return
    c = props.edit_constraints
    if c == 'connector':
        update_connector_constraints(props)
        return
    elif c == 'neighbor':
        update_neighbor_constraints(props)
        return
    elif c == 'grid':
        update_grid_constraints(props)
        return

    update_constraints(props, get_constraints(props))

def update_edit_form(_self, _context):
    props = bpy.context.scene.wfc_props
    default_obj = None
    obj = None
    if props.edit_type == 'defaults':
        obj = get_default_empty_object(props.collection_obj, True)
    elif props.edit_type == 'objects':
        sel_items = get_selected_items(props.obj_list)
        if len(sel_items) < 1: return
        obj = get_object_by_name(props, sel_items[0])
        default_obj = get_default_empty_object(props.collection_obj)
        if obj is None: obj = default_obj
        if obj is None: return

    if props.edit_constraints == '_none_': return

    auto_save = props.auto_save
    props.auto_save = False

    if props.edit_constraints == 'neighbor':
        props.vis_directions = is_directions_geometry_nodegroup_visible(obj)
        props.edit_neighbor_constraint = props.edit_neighbor_constraint
    elif props.edit_constraints == 'grid':
        pmap = {'corner' : 'wfc_corners', 'edge' : 'wfc_edges', 'face' : 'wfc_faces', 'inside' : 'wfc_inside'}
        for p,cp in pmap.items():
            if cp in obj or (default_obj and cp in default_obj):
                eo = default_obj
                if cp in obj: eo = obj
                props[p+"_none"] = eo[cp] == "-"
                vals = eo[cp].split(",")
                for c in vals: props[p+'_'+c] = True
                for a in { **FACE_DIRECTIONS, **CORNER_DIRECTIONS, **EDGE_DIRECTIONS }:
                    if '_' in a: a = a.split('_',1)[1]
                    if a.lower() not in vals: props[p+'_'+a.lower()] = False
            else:
                props[p+"_none"] = False
                for a in { **FACE_DIRECTIONS, **CORNER_DIRECTIONS, **EDGE_DIRECTIONS }:
                    if '_' in a: a = a.split('_', 1)[1]
                    props[p+'_'+a.lower()] = False
    elif props.edit_constraints == 'connector':
        props.vis_directions = is_directions_geometry_nodegroup_visible(obj)
        props.conn_directions = props.conn_directions

    else:
        lc = {}
        for c in GEN_CONSTRAINTS:
            cp = 'wfc_' + c.lower()
            if c in LIST_CONSTRAINTS:
                if LIST_CONSTRAINTS[c] in lc:
                    lc[LIST_CONSTRAINTS[c]].append(c)
                else:
                    lc[LIST_CONSTRAINTS[c]] = [ c ]
            elif cp in obj:
                try:
                    props[c] = obj[cp]
                except:
                    pass
            elif default_obj and cp in default_obj:
                try:
                    props[c] = default_obj[cp]
                except:
                    pass
            elif c in PROP_DEFAULTS:
                try:
                    props[c] = PROP_DEFAULTS[c]
                except:
                    pass
        for l in lc:
            li = getattr(props, l)
            li.clear()
            idx = 0
            while f"wfc_{lc[l][0]}_{idx}" in obj:
                item = li.add()
                for c in lc[l]:
                    try:
                        if c in ENUM_CONSTRAINTS:
                            setattr(item, c, ENUM_CONSTRAINTS[c][obj[f"wfc_{c}_{idx}"]])
                        else:
                            setattr(item, c, obj[f"wfc_{c}_{idx}"])
                    except TypeError as e:
                        v = obj[f"wfc_{c}_{idx}"]
                        print(f"set of constraint {c} failed for item {item}: {v}: {e}" )
                        pass
                idx += 1
    props.auto_save = auto_save


def handle_edit_neighbor_constraint_update(_self, context):
    props = context.scene.wfc_props
    if props.edit_neighbor_constraint == "_NONE_": return
    default_obj = None
    obj = None
    if props.edit_type == 'objects':
        sel_obj_list = get_selected_items(props.obj_list)
        if len(sel_obj_list) == 0: return
        obj = get_object_by_name(props, sel_obj_list[0])
        default_obj = get_default_empty_object(props.collection_obj)
    elif props.edit_type == 'defaults':
        obj = get_default_empty_object(props.collection_obj, True)
    else:
        return

    if obj and props.edit_neighbor_constraint not in obj and default_obj and props.edit_neighbor_constraint in default_obj:
        obj = default_obj

    auto_save = props.auto_save
    props.auto_save = False

    if obj and props.edit_neighbor_constraint in obj:
        vals = obj[props.edit_neighbor_constraint].split(",")
        props.no_neighbor_allowed = '-' in vals
        for item in props.neighbor_list: item.selected = item.obj.name in vals
    else:
        props.no_neighbor_allowed = False
        for item in props.neighbor_list: item.selected = False

    if obj and "wfc_allow_neighbor_constraint_violations" in obj:
        props.allow_neighbor_constraint_violations = obj["wfc_allow_neighbor_constraint_violations"]
    elif default_obj and "wfc_allow_neighbor_constraint_violations" in default_obj:
        props.allow_neighbor_constraint_violations = default_obj["wfc_allow_neighbor_constraint_violations"]
    else:
        props.allow_neighbor_constraint_violations = PROP_DEFAULTS["allow_neighbor_constraint_violations"]
    props.auto_save = auto_save

def handle_conn_directions_update(_self, _context):
    props = bpy.context.scene.wfc_props
    if props.conn_directions == '_NONE_': return
    obj = None
    if props.edit_type == 'objects':
        selected = get_selected_items(props.obj_list)
        if len(selected) == 0: return
        obj = get_object_by_name(props, selected[0])
    elif props.edit_type == 'defaults':
        obj = get_default_empty_object(props.collection_obj)
    auto_save = props.auto_save
    props.auto_save = False
    props.conn_name = obj.get(props.conn_directions, '')
    props.auto_save = auto_save

def get_default_empty_name():
    prefs =  bpy.context.preferences.addons[__package__].preferences
    return prefs.default_empty_name if prefs.default_empty_name != "" else DEFAULT_EMPTY_NAME

def cmpall(a, b):
    try:
        iter(a)
        iter(b)
        return all(x == y for x, y in zip(a, b))
    except TypeError:
        return a == b

def handle_update_collection(_self, context = None):
    props = context.scene.wfc_props if context is not None else bpy.context.scene.wfc_props
    if props.collection_obj is None: return
    sel_items = get_selected_items(props.obj_list)
    sel_n_items = get_selected_items(props.neighbor_list)
    sel_rt_items = get_selected_items(props.rt_list)
    props.obj_list.clear()
    props.neighbor_list.clear()
    props.rt_list.clear()
    coll_objects_obj = [obj for obj in props.collection_obj.objects if
                    not obj.name.startswith(get_default_empty_name())]
    coll_objects_obj.sort(key=lambda x: x.name)
    coll_objects = [child for child in props.collection_obj.children]
    coll_objects.sort(key=lambda x: x.name)
    coll_objects.extend(coll_objects_obj)
    for obj in coll_objects:
        if obj.name.startswith(get_default_empty_name()): continue
        item = props.obj_list.add()
        item.obj = obj
        item.selected = obj.name in sel_items
        item = props.neighbor_list.add()
        item.obj = obj
        item.selected = obj.name in sel_n_items
        item = props.rt_list.add()
        item.obj = obj
        item.selected = obj.name in sel_rt_items

def get_noise_basis(_self, _context = None):
    ret = [('_NONE_','Please select a noise basis','Please select a noise basis'),None]
    for nb in ['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']:
        ret.append((nb,nb,nb))
    return ret

def remap(x, in_min, in_max, out_min, out_max):
    return out_min + (float(x - in_min) / (in_max - in_min)) * (out_max - out_min)

def get_noise(pos, basis, scale, minv = None, maxv = None):
    nb = get_noise_basis(None)
    if basis < 2 or basis >= len(nb): basis = 3
    v = Vector(((pos[0]+1) * scale, (pos[1]+1) * scale, (pos[2]+1) * scale))
    n = noise.noise(v, noise_basis=nb[basis][0])
    if minv is None or maxv is None: return n
    return remap(n, -1, 1, minv, maxv)

def set_select_all_list_items(itemlist, selected):
    for item in itemlist:
        item.selected = selected
