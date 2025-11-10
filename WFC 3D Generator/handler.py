import bpy
from .helper import get_default_empty_name, get_selected_items

def _update_list(itemlist, selected_object_names):
    # caution: any item.selected change fires an event => only do necessary updates
    for item in itemlist:
        if item.obj.name in selected_object_names:
            if not item.selected:
                item.selected = True
        elif item.selected:
            item.selected = False


def update_handler(_scene, _depsgraph):
    props = bpy.context.scene.wfc_props
    # handle collection changes:
    if props.collection_obj is not None:
        coll_objects = [obj for obj in props.collection_obj.objects if
                        not obj.name.startswith(get_default_empty_name())]
        coll_objects.extend([child for child in props.collection_obj.children])
        if len(coll_objects) != len(props.obj_list):
            sel_items = get_selected_items(props.obj_list)
            sel_n_items = get_selected_items(props.neighbor_list)
            props.obj_list.clear()
            props.neighbor_list.clear()
            for obj in coll_objects:
                item = props.obj_list.add()
                item.obj = obj
                item.selected = obj.name in sel_items
                item = props.neighbor_list.add()
                item.obj = obj
                item.selected = obj.name in sel_n_items

    if props.collection_obj is None or (not props.auto_active_object and not props.auto_neighbor_object): return

    # handle selections:
    view_layer = bpy.context.view_layer
    selected_objects = [obj for obj in view_layer.objects if obj.select_get()]
    if selected_objects is not None:
        selected_object_names = []
        for obj in selected_objects:
            if obj.name in props.collection_obj.objects:
                selected_object_names.append(obj.name)
            else:
                selected_object_names.extend([child.name for child in props.collection_obj.children if obj.name in child.objects])
        if props.auto_active_object:
            _update_list(props.obj_list, selected_object_names)
        elif props.auto_neighbor_object:
            _update_list(props.neighbor_list, selected_object_names)
