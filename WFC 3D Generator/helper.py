from typing import Any
import bpy
from .constants import *

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
                if props[prop_name + "_" + v]:
                    newval.append(v)
        return ",".join(newval)

    def _set_grid_constraints(obj, props):
        obj["wfc_corners"] = _get_new_prop_val(props, "corner",
                                               ['fbl', 'fbr', 'ftl', 'ftr', 'bbl', 'bbr', 'btl', 'btr'])
        obj["wfc_edges"] = _get_new_prop_val(props, "edge",
                                             ['fb', 'fl', 'fr', 'ft', 'bb', 'bl', 'br', 'bt', 'lb', 'lt', 'rb',
                                              'rt'])
        obj["wfc_faces"] = _get_new_prop_val(props, "face", ['front', 'back', 'top', 'bottom', 'left', 'right'])
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
