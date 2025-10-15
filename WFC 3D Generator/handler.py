import bpy

def on_object_activated(scene, depsgraph):
    if bpy.context.view_layer.objects.active:
        active_object = bpy.context.view_layer.objects.active
        props = bpy.context.scene.wfc_props
        if not props.collection_obj:
            return
        if active_object.name in props.collection_obj.objects or active_object.name in props.collection_obj.children:
            if props.auto_active_object:
                if props.edit_object != active_object.name:
                    props.edit_object = active_object.name
            elif props.auto_neighbor_object:
                if props.select_neighbor != active_object.name:
                    props.select_neighbor = active_object.name