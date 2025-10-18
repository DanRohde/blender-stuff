import bpy

def _update_list(list, selected_object_names):
    # caution: any item.sected change fires an event => only do necessary updates
    for item in list:
        if item.name in selected_object_names:
            if not item.selected:
                item.selected = True
        elif item.selected:
            item.selected = False

def update_handler(scene, depsgraph):
    if bpy.context.view_layer.objects.active:
        props = bpy.context.scene.wfc_props

        if props.collection_obj is None and ( not props.auto_active_object and not props.auto_neighbor_object ):
            return
        
        # handle collection changes:
        coll_objects = list(props.collection_obj.objects)
        coll_objects.extend([ child for child in props.collection_obj.children if len(child.objects)>0])
        if len(coll_objects) != len(props.obj_list):
            props.obj_list.clear()
            props.neighbor_list.clear()
            for obj in coll_objects:
                item = props.obj_list.add()
                item.name = obj.name
                item = props.neighbor_list.add()
                item.name = obj.name
                item.value = obj.name

        # handle selections:
        selected_objects = bpy.context.selected_objects
        if selected_objects:
            selected_object_names = [ ]
            for obj in selected_objects: 
                if obj.name in props.collection_obj.objects:
                    selected_object_names.append(obj.name)
                else:
                    for child in props.collection_obj.children:
                        if obj.name in child.objects:
                            selected_object_names.append(child.name)
            if props.auto_active_object:
                _update_list(props.obj_list, selected_object_names)
            elif props.auto_neighbor_object:
                _update_list(props.neighbor_list, selected_object_names)
