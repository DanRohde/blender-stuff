from typing import Any
import bpy
from .constants import *
from .vis import is_directions_geometry_nodegroup_visible

def get_default_empty_object(collection: object, create: object = False) -> Any | None:
    if DEFAULT_EMPTY_NAME in collection.objects:
        return collection.objects[DEFAULT_EMPTY_NAME]
    else:
        for o in collection.objects:
            if o.name.startswith(DEFAULT_EMPTY_NAME):
                return o
        if not create: return None
        obj = bpy.data.objects.new(DEFAULT_EMPTY_NAME, None)
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
        constraints = [props.edit_neighbor_constraint]
    elif props.edit_constraints == 'connector':
        constraints = CONNECTOR_CONSTRAINTS
    return constraints

def get_selected_items(obj_list):
    return [item.name for item in obj_list if item.selected]

def update_constraints(props, constraints):
    items = []
    if props.edit_type == 'objects':
        items = get_selected_items(props.obj_list)
    elif props.edit_type == 'defaults':
        items = [DEFAULT_EMPTY_NAME]

    for item in items:
        obj = get_object_by_name(props, item)
        for c in constraints:
            if c in props:
                if props[c] != PROP_DEFAULTS[c]:
                    obj["wfc_" + c] = props[c]
                elif "wfc_" + c in obj:
                    del obj["wfc_" + c]

def update_connector_constraints(props):
    prop_name = props.conn_directions
    connector = props.conn_name
    if prop_name == '_NONE_': return
    if props.edit_type == 'objects':
        for item in get_selected_items(props.obj_list):
            obj = get_object_by_name(props, item)
            obj[prop_name] = connector
    elif props.edit_type == 'defaults':
        obj = get_object_by_name(props, DEFAULT_EMPTY_NAME)
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
        _set_grid_constraints(get_object_by_name(props, DEFAULT_EMPTY_NAME), props)

def update_neighbor_constraints(props):
    def _set_neighbors(obj, prop_name, neighbors):
        obj[prop_name] = ",".join(neighbors)

    prop_name = props.edit_neighbor_constraint
    if props.no_neighbor_allowed:
        neighbors = ["-"]
    else:
        neighbors =  [item.value for item in props.neighbor_list if item.selected]
    if props.edit_type == 'objects':
        for item in get_selected_items(props.obj_list):
            obj = get_object_by_name(props, item)
            update_constraints(props, ADD_NEIGHBOR_CONSTRAINTS)
            _set_neighbors(obj, prop_name, neighbors)
    elif props.edit_type == 'defaults':
        obj = get_object_by_name(props, DEFAULT_EMPTY_NAME)
        update_constraints(props, ADD_NEIGHBOR_CONSTRAINTS)
        _set_neighbors(obj, prop_name, neighbors)

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

def update_edit_form(self, _context):
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
                for a in DIRECTIONS:
                    if '_' in a: a = a.split('_',1)[1]
                    if a.lower() not in vals: props[p+'_'+a.lower()] = False
            else:
                props[p+"_none"] = False
                for a in DIRECTIONS:
                    if '_' in a: a = a.split('_', 1)[1]
                    props[p+'_'+a.lower()] = False
    elif props.edit_constraints == 'connector':
        props.vis_directions = is_directions_geometry_nodegroup_visible(obj)
        props.conn_directions = props.conn_directions
    else:
        for c in SYMMETRY_CONSTRAINTS + TRANSFORMATION_CONSTRAINTS + FREQUENCY_CONSTRAINTS + PROBABILITY_CONSTRAINTS + REGION_CONSTRAINTS:
            cp = 'wfc_' + c.lower()
            if cp in obj:
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
        for item in props.neighbor_list: item.selected = item.value in vals
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