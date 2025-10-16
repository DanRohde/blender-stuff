import bpy

last_objects = set()
last_children = set()
def on_object_activated(scene, depsgraph):
    global last_objects
    global last_children
    props = bpy.context.scene.wfc_props
    
#    if props.collection_obj is not None:
#        current_objects = set(props.collection_obj.objects)
#        current_children = set(props.collection_obj.children)
#        print("current_objects",current_objects)
#        if current_objects != last_objects:
#            removed = last_objects - current_objects
#            added = current_objects - last_objects
#            print("added:",added)
#            print("removed:",removed)
#            if added:
#                for obj in added:
#                    item = props.obj_list.add()
#                    item.name = obj.name
#            if removed:
#                for obj in removed:
#                    for i in range(len(props.obj_list)-1,-1,-1):
#                        if props.obj_list[i].name == obj.name:
#                            props.obj_list.remove(i)
#            last_objects = current_objects.copy()
#        if current_children != last_children:
#            removed = last_children - current_children
#            added = current_children - last_children
#            last_children = current_children.copy()
#            if added:
#                for obj in added:
#                    item = props.obj_list.add()
#                    item.name = obj.name
#            if removed:
#                for obj in removed:
#                    for i in range(len(props.obj_list)-1,-1,-1):
#                        if props.obj_list[i].name == obj.name:
#                            props.obj_list.remove(i)        
#                 
    if bpy.context.view_layer.objects.active:
        active_object = bpy.context.view_layer.objects.active
        if not props.collection_obj:
            return
        if active_object.name in props.collection_obj.objects or active_object.name in props.collection_obj.children:
            if props.auto_active_object:
                if props.edit_object != active_object.name:
                    props.edit_object = active_object.name
            elif props.auto_neighbor_object:
                if props.select_neighbor != active_object.name:
                    props.select_neighbor = active_object.name