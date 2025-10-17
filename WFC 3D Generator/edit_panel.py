import bpy
from .constants import ICON_MAP

class WFC3D_UL_EditPanelMultiSelList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        props = context.scene.wfc_props
        if item.name in props.collection_obj.objects:
            icon_name = ICON_MAP[props.collection_obj.objects[item.name].type]
        else:
            icon_name = "GROUP"
            
        row = layout.row(align=True)
        row.prop(item, "selected", text=item.name, icon=icon_name)

class WFC3D_UL_EditPanelNeighborMultiSelList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        props = context.scene.wfc_props
        if item.value in props.collection_obj.objects:
            icon_name = ICON_MAP[props.collection_obj.objects[item.value].type]
        else:
            icon_name = "GROUP"
            
        row = layout.row(align=True)
        row.prop(item, "selected", text=item.name, icon=icon_name)
    

class WFC3D_PT_EditPanel(bpy.types.Panel):
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
        if not props.collection_obj:
            layout.label(text="Choose a Source Collection", icon='INFO')
            return
        
       
        row = col.row()
        newcol = row.column()

        newrow = col.box().row()
        nc=newrow.column()
        nc.operator("collection.wfc_get_selected_object", icon="SELECT_SET")
        nc.prop(props,"auto_active_object", icon="TRIA_RIGHT")
        nc=newrow.column()
        nc.template_list("WFC3D_UL_EditPanelMultiSelList","", props, "obj_list", props, "obj_list_idx")
        nc.enabled = not props.auto_active_object
        nc=newrow.column()
        nc.operator("collection.wfc_select_dropdown_object", icon='RESTRICT_SELECT_OFF')
        nc.operator("collection.wfc_collection_list_select_all", icon="CHECKBOX_HLT")
        nc.operator("collection.wfc_collection_list_select_none", icon="CHECKBOX_DEHLT")
        nc.operator("collection.wfc_update_collection_list",icon="FILE_REFRESH")
        nc.enabled = not props.auto_active_object
        
        if len(props.obj_list) == 0:
            newrow.label(text="Empty Collection")
            
            return
            
        selected = [item.name for item in props.obj_list if item.selected]
        if len(selected) == 0:
            return
            
            
        row = col.row()
        
        if selected[0] in props.collection_obj.children:
            obj = props.collection_obj.children[selected[0]].objects[0]
        else:
            obj = props.collection_obj.objects[selected[0]]
            
        obj_name = ",".join(selected)
        
        box = row.box()
        
        box.label(text=obj_name, icon="OBJECT_DATA")
        
        box.prop(props,"edit_constraints",icon="SETTINGS")
        
        if (props.edit_constraints == "neighbor"):
            box=col.box()
            row = box.row()
            row.label(icon="CUBE",text="")
            row.prop(props,"edit_neighbor_constraint")
            newrow = row.row()
            newrow.operator("object.wfc_reset_constraint")
            newrow.enabled = props.edit_neighbor_constraint in obj;
            
            if (props.edit_neighbor_constraint and props.edit_neighbor_constraint !="_none_"):
                if props.edit_neighbor_constraint in obj:  
                    box.label(text="Neighbors: "+obj[props.edit_neighbor_constraint])
                else:
                    box.label(text="Neighbors:")
                
                box.box().prop(props,"no_neighbor_allowed",icon="VIEW_LOCKED")
                row = box.box().row()
                row.enabled = not props.no_neighbor_allowed 
                newcol = row.column()
                newcol.operator("collection.wfc_get_neighbor_selected_object", icon="SELECT_SET")
                nc=newcol.column();
                nc.prop(props,"auto_neighbor_object",icon="TRIA_RIGHT")
                nc.enabled = not props.auto_active_object
                newcol = row.column()
                newcol.template_list("WFC3D_UL_EditPanelNeighborMultiSelList", "", props, "neighbor_list", props, "neighbor_list_idx")
                newcol.enabled = not props.auto_neighbor_object
                newcol = row.column()
                newcol.enabled = not props.auto_neighbor_object
                nr = newcol.row()
                nr.operator("collection.wfc_select_neighbor_object", icon='RESTRICT_SELECT_OFF')
                nr.enabled = not props.auto_active_object
                newcol.operator("collection.wfc_neighbor_list_select_all", icon="CHECKBOX_HLT")
                newcol.operator("collection.wfc_neighbor_list_select_none", icon="CHECKBOX_DEHLT")
        
                row=box.row()
                row.operator("object.wfc_save_constraint")
        if (props.edit_constraints == "grid"):    
            box=col.box()
            row = box.row()
            row.label(text=obj_name)
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
            box.prop(props,"probability")
            box.prop(props, "weight")
            
            box.operator("object.wfc_update_probability_constraints")    
        if (props.edit_constraints == "transformation"):
            box=col.box()
            row = box.row()
            row.label(text=obj_name)
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
        if (props.edit_constraints=="frequency"):
            box = col.box()
            row=box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_frequency_constraints")
            
            newbox = box.box()
            newbox.label(text="Same Object")
            newbox.prop(props,"freq_grid")
            newbox.prop(props,"freq_neighbor")
            newbox.prop(props,"freq_neighbor_face")
            newbox.prop(props,"freq_neighbor_corner")
            newbox.prop(props,"freq_neighbor_edge")
            row = newbox.row()
            row.prop(props,"freq_axes")
            
            newbox = box.box()
            newbox.label(text="Any Object")
            newbox.prop(props,"freq_any_neighbor")
            newbox.prop(props,"freq_any_neighbor_face")
            newbox.prop(props,"freq_any_neighbor_corner")
            newbox.prop(props,"freq_any_neighbor_edge")
            
            row = newbox.row()
            row.prop(props,"freq_any_axes")
            
            box.operator("object.wfc_update_frequency_constraints")
            
        if (props.edit_constraints=="symmetry"):
            box = col.box()
            box.label(text=obj_name)
            box.label(text="Symmetry Constraints")
            
            box.label(text="Mirror Symmetry")
            box.label(text="Rotational Symmetry")
            box.label(text="Translational Symmetry")
            box.label(text="Point Reflection Symmetry")
            box.label(text="Glide Reflection Symmetry")
        

panels = [ WFC3D_UL_EditPanelMultiSelList, WFC3D_UL_EditPanelNeighborMultiSelList, WFC3D_PT_EditPanel,]

        