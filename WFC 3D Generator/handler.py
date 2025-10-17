import bpy

def on_object_activated(scene, depsgraph):
    if bpy.context.view_layer.objects.active:
        active_object = bpy.context.view_layer.objects.active
        ao_name = active_object.name
        props = bpy.context.scene.wfc_props
        if not props.collection_obj or ( not props.auto_active_object and not props.auto_neighbor_object ):
            return
        
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
                for item in props.obj_list:
                    if item.name in selected_object_names:
                        if not item.selected:
                            item.selected = True 
                    elif item.selected:
                        item.selected = False
                    
            elif props.auto_neighbor_object:
                for item in props.neighbor_list:
                    if item.value in selected_object_names:
                        if not item.selected:
                            item.selected = True
                    elif item.selected:
                        item.selected = False
            