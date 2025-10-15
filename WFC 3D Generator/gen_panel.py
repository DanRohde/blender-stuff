import bpy
class WFC3DGeneratePanel(bpy.types.Panel):
    """User interface for WFC 3D Add-On"""
    bl_label = "WFC 3D Generator"
    bl_idname = "VIEW3D_PT_wfc_3d"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Gen'

    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        
        layout.label(text="Source Collection")
        
        layout.prop(props, "collection_obj")
       
        box = layout.box()
       
        box.label(text="Grid Size (width/depth/height)")
        box.row().prop(props, "grid_size")
        box.label(text="Grid Cell Space")
        box.row().prop(props, "spacing")
        
        box.prop(props, "use_constraints")
        
        layout.label(text="Target Collection")
        box = layout.box()
        box.prop(props, "target_collection")
        box.prop(props, "link_objects")
        row=box.row()
        row.prop(props, "copy_modifiers")
        row.enabled = props.link_objects
        box.prop(props, "remove_target_collection")
        
        layout.prop(props, "seed")

        layout.separator(type="LINE", factor=0.2)

        if props.remove_target_collection and props.target_collection != "" and props.target_collection in bpy.data.collections:
            layout.box().label(text="Target collection will be removed!", icon="WARNING_LARGE")
            

        row = layout.row();
        row.enabled = props.collection_obj!=None and ( (len(props.collection_obj.objects)>0)or(len(props.collection_obj.children)>0) ) and props.collection_obj.name != props.target_collection
        row.operator("object.wfc_3d_generate")
        if props.collection_obj is None:
            layout.label(text="Please select a source collection.", icon="INFO_LARGE")
        if props.collection_obj is not None and props.collection_obj.name == props.target_collection:
            layout.label(text="Source and target collection should not be the same.", icon="WARNING_LARGE")
        if props.collection_obj and len(props.collection_obj.objects)==0 and len(props.collection_obj.children)==0:
            layout.label(text="Please select a non-empty source collection.", icon="INFO_LARGE")
            


panels = [ WFC3DGeneratePanel ]
