import bpy

class WFC3DEditPanel(bpy.types.Panel):
    """User interface for WFC 3D Add-On"""
    bl_label = "WFC 3D Constraint Editor"
    bl_idname = "VIEW3D_PT_wfc_3d_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Edit'

    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        layout.label(text="Source Collection")
        layout.prop(props, "collection_obj")
        col = layout.column(align=True)
        if props.collection_obj:
            row = col.row()
            box = row.box()
            box.label(text="Object")
            row = box.row()
            row.operator("collection.wfc_get_selected_object", icon="SELECT_SET")
            row.prop(props,"auto_active_object")
            newcol = row.column()
            newcol.prop(props, "edit_object")
            newcol.enabled = not props.auto_active_object
            newcol = row.column()
            newcol.operator("collection.wfc_select_dropdown_object", icon='RESTRICT_SELECT_OFF')
            newcol.enabled = props.edit_object and props.edit_object != '_none_' and not props.auto_active_object
            
            row = col.row()
            row.enabled = False
            if props.edit_object and props.edit_object != '_none_':
                row.enabled = True

                if props.edit_object in props.collection_obj.children:
                    obj=props.collection_obj.children[props.edit_object].objects[0]
                else:
                    obj=props.collection_obj.objects[props.edit_object]
                    
                row=col.row();
                row.box().prop(props,"edit_constraints")
                if (props.edit_constraints == "neighbor"):
                    box=col.box()
                    box.label(text="Neighbor Constraints")
                    row = box.row()
                    row.prop(props,"edit_neighbor_constraint")
                    newrow = row.row()
                    newrow.operator("object.wfc_reset_constraint")
                    newrow.enabled = props.edit_neighbor_constraint in obj;
                    
                    if (props.edit_neighbor_constraint and props.edit_neighbor_constraint !="_none_"):
                        if props.edit_neighbor_constraint in obj:  
                            box.label(text="Neighbors: "+obj[props.edit_neighbor_constraint])
                        else:
                            box.label(text="Neighbors:")
                        row = box.row()
                        row.operator("collection.wfc_get_neighbor_selected_object", icon="SELECT_SET")
                        newcol = row.column()
                        newcol.enabled = not props.auto_active_object
                        newcol.prop(props,"auto_neighbor_object")
                        newcol = row.column()
                        newcol.prop(props,"select_neighbor")
                        newcol.enabled = not props.auto_neighbor_object or props.auto_active_object
                        newcol = row.column()
                        newcol.enabled = not props.auto_active_object and not props.auto_neighbor_object and props.select_neighbor != '_none_'
                        newcol.operator("collection.wfc_select_neighbor_object", icon='RESTRICT_SELECT_OFF')
                        row=box.row()
                        if (props.select_neighbor and props.select_neighbor != '_none_'):
                            row.operator("object.wfc_add_constraint", icon='ADD')
                            row.operator("object.wfc_remove_constraint", icon='REMOVE')
                if (props.edit_constraints == "grid"):    
                    box=col.box()
                    row = box.row()
                    row.label(text="Grid Constraints")
                    row.operator("object.wfc_reset_grid_constraints")
                    newbox = box.box()
                    newrow = newbox.row()
                    newrow.label(text="Corners")
                    newrow.prop(props, "corner_none")    
                    if not props.corner_none:
                        row = newbox.row()
                        for c in ['fbl','fbr','ftl','ftr']:
                            row.prop(props,"corner_"+c)
                            
                        row = newbox.row()
                        for c in ['bbl','bbr','btl','btr']:
                            row.prop(props,"corner_"+c)
                    
                    newbox = box.box()
                    newrow = newbox.row()
                    newrow.label(text="Edges")
                    newrow.prop(props,"edge_none")
                    if not props.edge_none:
                        for p in ['f','b']:
                            row = newbox.row()
                            for c in ['b','l','t','r']:
                                row.prop(props,"edge_"+p+c)
                        row = newbox.row()
                        for p in ['lb','lt','rb','rt']:
                            row.prop(props,"edge_"+p)
                    
                    newbox = box.box()
                    newrow = newbox.row()
                    newrow.label(text="Faces")
                    newrow.prop(props, "face_none")
                    if not props.face_none:
                        row = newbox.row()
                        for f in ['front','left','top']:
                            row.prop(props, "face_"+f)
                        row = newbox.row()
                        for f in ['back','right','bottom']:
                            row.prop(props,"face_"+f)
                        
                    
                    newbox = box.box()
                    newrow = newbox.row()
                    newrow.label(text="Inside")
                    newrow.prop(props,"inside_none")
                    
                    
                    box.operator("object.wfc_update_grid_constraints")
                if (props.edit_constraints == "probability"):
                    box=col.box()
                    box.label(text="Weight Constraints")
                    newbox = box.box()
                    newbox.prop(props, "weight")
                    
                    box.operator("object.wfc_update_probability_constraints")    
                if (props.edit_constraints == "transformation"):
                    box=col.box()
                    row = box.row()
                    row.label(text="Transformations")
                    row.operator("object.wfc_reset_transformation_constraints")
                    newbox = box.box()
                    newbox.label(text="Translation")
                    newbox.row().prop(props,"translation_min")
                    newbox.row().prop(props,"translation_max")
                    newbox.row().prop(props,"translation_steps")

                    newbox = box.box()
                    newbox.label(text="Rotation")
                    newbox.row().prop(props,"rotation_min")
                    newbox.row().prop(props,"rotation_max")
                    newbox.row().prop(props,"rotation_steps")
                    #newbox.row().prop(props,"rotation_neighbor")
                    #newbox.row().prop(props,"rotation_grid")

                    newbox = box.box()
                    newrow = newbox.row()
                    newrow.label(text="Scale")
                    newrow.prop(props,"scale_type")
                    if props.scale_type == 'uniform':
                        newbox.prop(props,"scale_uni")
                    elif props.scale_type == 'non-uniform':
                        newbox.row().prop(props,"scale_min")
                        newbox.row().prop(props,"scale_max")
                        newbox.row().prop(props,"scale_steps")

                    box.operator('object.wfc_update_transformation_constraints')
                if (props.edit_constraints=="symmetry"):
                    box = col.box()
                    box.label(text="Symmetry Constraints")
                    
                    box.label(text="Mirror Symmetry")
                    box.label(text="Rotational Symmetry")
                    box.label(text="Translational Symmetry")
                    box.label(text="Point Reflection Symmetry")
                    box.label(text="Glide Reflection Symmetry")
        else:
            layout.label(text="Choose a Source Collection", icon='INFO')

panels = [ WFC3DEditPanel ]

        