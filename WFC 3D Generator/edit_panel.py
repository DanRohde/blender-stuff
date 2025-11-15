import bpy
from .helper import get_default_empty_object, get_icon_name, cmpall, get_selected_items, get_object_by_name
from .properties import get_known_conn_names
from .constants import *

class WFC3D_UL_EditPanelMultiSelList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        layout.row(align=True).prop(item, "selected", text=item.obj.name, icon=get_icon_name(item))


class WFC3D_UL_EditPanelNeighborMultiSelList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        layout.row(align=True).prop(item, "selected", text=item.obj.name, icon=get_icon_name(item))

class WFC3D_UL_RegFreqList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        row = layout.row(align=True)
        col = row.column(align=True)
        col.label(text=f"{index}.")
        col.prop(item,"selected", text="")
        col = row.column(align=True)
        col.row().prop(item,"regfreq_min")
        col.row().prop(item,"regfreq_max")
        col.row().prop(item,"regfreq_freq")

class WFC3D_UL_FixedPositionList(bpy.types.UIList):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        row = layout.row(align=True)
        row.prop(item,"selected", text="")
        row.prop(item,"fixed_position_xyz")

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
        
        if len(props.obj_list) == 0:
            layout.label(text="Empty Collection")
            return
            
        box = col.box()
        box.prop(props,"edit_type", icon="OBJECT_DATA")

        selected = []
        if props.edit_type == 'objects':
            newrow = box.row()
            nc=newrow.column().box()
            nc.operator("collection.wfc_get_selected_object", icon="SELECT_SET")
            nc.prop(props,"auto_active_object", icon="TRIA_RIGHT")
            nc=newrow.column()
            nc.template_list("WFC3D_UL_EditPanelMultiSelList","", props, "obj_list", props, "obj_list_idx")
            nc.enabled = not props.auto_active_object
            nc=newrow.column().box()
            nc.operator("collection.wfc_select_dropdown_object", icon='RESTRICT_SELECT_OFF')
            nc.operator("collection.wfc_collection_list_select_all", icon="CHECKBOX_HLT")
            nc.operator("collection.wfc_collection_list_select_none", icon="CHECKBOX_DEHLT")
            nc.operator("collection.wfc_update_collection_list",icon="FILE_REFRESH")
            nc.enabled = not props.auto_active_object
        
            selected =get_selected_items(props.obj_list)
            if len(selected) == 0 and props.edit_type == 'objects':
                return

        obj = None
        obj_name = ""
        if props.edit_type == 'objects':
            if selected[0] in props.collection_obj.children:
                obj = get_object_by_name(props, selected[0])
            elif selected[0] in props.collection_obj.objects:
                obj = props.collection_obj.objects[selected[0]]
            else:
                box.label(text="Selected object not found! Please press the reload button.")
                return
            obj_name = ",".join(selected)
            box.label(text=obj_name, icon="OBJECT_DATA")
            
        elif props.edit_type == 'defaults':
            obj = get_default_empty_object(props.collection_obj)
            obj_name = 'Collection Defaults'

        row = box.box().row()
        row.operator('collection.wfc_info_toggle',icon='INFO_LARGE', depress = props.info_toggle)
        row.prop(props,"edit_constraints",icon="SETTINGS")
        row.operator('collection.wfc_auto_save_toggle',icon='IMPORT',depress = props.auto_save)

        if props.info_toggle: self.draw_info_panel(layout, props, obj)
        if props.edit_constraints == "neighbor":
            box = box.box()
            row = box.row()
            row.prop(props,"edit_neighbor_constraint")
            col = row.column()
            col.operator("object.wfc_vis_directions", text="", icon="CUBE", depress=props.vis_directions)
            col.enabled = props.edit_type == 'objects'

            newrow = row.row()
            newrow.operator("object.wfc_reset_constraints",text="",icon="PRESET")
            newrow.enabled = props.edit_type == 'defaults' or (obj and props.edit_neighbor_constraint in obj)
            
            if props.edit_neighbor_constraint and props.edit_neighbor_constraint !="_NONE_":
                if obj and props.edit_neighbor_constraint in obj:
                    box.label(text="Neighbors: "+obj[props.edit_neighbor_constraint])
                else:
                    box.label(text="Neighbors:")
                
                box.prop(props,"no_neighbor_allowed",icon="VIEW_LOCKED")
                row = box.row()
                row.enabled = not props.no_neighbor_allowed 
                newcol = row.column().box()
                newcol.operator("collection.wfc_get_neighbor_selected_object", icon="SELECT_SET")
                nc=newcol.column()
                nc.prop(props,"auto_neighbor_object",icon="TRIA_RIGHT")
                nc.enabled = not props.auto_active_object
                newcol = row.column()
                newcol.template_list("WFC3D_UL_EditPanelNeighborMultiSelList", "", props, "neighbor_list", props, "neighbor_list_idx")
                newcol.enabled = not props.auto_neighbor_object
                newcol = row.column().box()
                newcol.enabled = not props.auto_neighbor_object
                nr = newcol.row()
                nr.operator("collection.wfc_select_neighbor_object", icon='RESTRICT_SELECT_OFF')
                nr.enabled = not props.auto_active_object
                newcol.operator("collection.wfc_neighbor_list_select_all", icon="CHECKBOX_HLT")
                newcol.operator("collection.wfc_neighbor_list_select_none", icon="CHECKBOX_DEHLT")

                box.row().prop(props,"allow_neighbor_constraint_violations",icon="VIEW_UNLOCKED")

                if not props.auto_save: box.row().operator("object.wfc_update_neighbor_constraints")
            if obj and not props.info_toggle:
                newbox = box.box()
                newbox.label(text=f"Defined neighbor constraints:")
                c=0
                for d in DIRECTIONS:
                    if 'wfc_' + d.lower() not in obj: continue
                    c+=1
                    newbox.label(text=f"{DIR_TRANSLATION[d]}: {obj['wfc_' + d.lower()]}")
                if c==0: newbox.label(text="nothing defined yet")
        if props.edit_constraints == "grid":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
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
            
            
            if not props.auto_save: box.operator("object.wfc_update_grid_constraints")
        if props.edit_constraints == 'region':
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
            row=box.row()
            row.prop(props,"region_min")
            row=box.row()
            row.prop(props,"region_max")

            
            box.row().label(text="Quadrant")
            box.row().prop(props, "region_quadrant",text="")

            if not props.auto_save: box.operator("object.wfc_update_constraints")
        if props.edit_constraints == "probability":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
            box.prop(props,"probability")
            box.prop(props, "weight")
            box.prop(props, "auto_weight", icon="MOD_VERTEX_WEIGHT")
            
            if not props.auto_save: box.operator("object.wfc_update_constraints")
        if props.edit_constraints == "transformation":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
            newbox = box.box()
            newbox.label(text="Translation Offset")
            newbox.row().prop(props,"translation_min")
            newbox.row().prop(props,"translation_max")
            newbox.row().prop(props,"translation_steps")

            newbox = box.box()
            newbox.label(text="Rotation")
            newbox.row().prop(props,"rotation_min")
            newbox.row().prop(props,"rotation_max")
            newbox.row().prop(props,"rotation_steps")

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

            newbox = box.box()
            newrow = newbox.row()
            newrow.prop(props,"flipping")
            if not props.auto_save: box.operator('object.wfc_update_constraints')
        if props.edit_constraints == "frequency":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
            
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
            
            if not props.auto_save: box.operator("object.wfc_update_constraints")

        if props.edit_constraints=="symmetry":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")

            box.label(text="Mirror Symmetry")
            newbox = box.box()
            newbox.row().prop(props,"sym_mirror_axes")
            if props.edit_type == 'objects':
                if props.sym_mirror_axes[0]: newbox.prop(props,"sym_mirror_axes_x", text="X Partner")
                if props.sym_mirror_axes[1]: newbox.prop(props,"sym_mirror_axes_y", text="Y Partner")
                if props.sym_mirror_axes[2]: newbox.prop(props,"sym_mirror_axes_z", text="Z Partner")
                if props.sym_mirror_axes[0] and props.sym_mirror_axes[1]: newbox.prop(props,"sym_mirror_axes_xy", text="XY Partner")
                if props.sym_mirror_axes[0] and props.sym_mirror_axes[2]: newbox.prop(props,"sym_mirror_axes_xz", text="XZ Partner")
                if props.sym_mirror_axes[1] and props.sym_mirror_axes[2]: newbox.prop(props,"sym_mirror_axes_yz", text="YZ Partner")
                if props.sym_mirror_axes[0] and props.sym_mirror_axes[1] and props.sym_mirror_axes[2]: newbox.prop(props,"sym_mirror_axes_xyz", text="XYZ Partner")

            if sum(props['sym_mirror_axes']) > 0:
                newbox.row().label(text="Flip Mirror Partner")
                fmpbox = newbox.box()
                row = fmpbox.column_flow(columns=4,align=True)
                if props.sym_mirror_axes[0]: row.prop(props,"sym_mirror_flip_x")
                if props.sym_mirror_axes[1]: row.prop(props,"sym_mirror_flip_y")
                if props.sym_mirror_axes[2]: row.prop(props,"sym_mirror_flip_z")
                if props.sym_mirror_axes[0] and props.sym_mirror_axes[1]: row.prop(props,"sym_mirror_flip_xy")
                if props.sym_mirror_axes[0] and props.sym_mirror_axes[2]: row.prop(props,"sym_mirror_flip_xz")
                if props.sym_mirror_axes[1] and props.sym_mirror_axes[2]: row.prop(props,"sym_mirror_flip_yz")
                if props.sym_mirror_axes[0] and props.sym_mirror_axes[1] and props.sym_mirror_axes[2]: row.prop(props,"sym_mirror_flip_xyz")

                flip = sum([props['sym_mirror_flip_'+k] for k in ['x','y','z','xy','xz','yz','xyz']])
                if flip > 0: fmpbox.row().prop(props,"sym_mirror_flip_transl")

                newbox.row().prop(props,"sym_mirror_trans")

            box.label(text="Rotational Symmetry")
            newbox = box.box()
            newbox.row().prop(props,"sym_rotate_axis")
            newbox.prop(props,"sym_rotate_n")

            if not props.auto_save: box.operator("object.wfc_update_constraints")

            #box.label(text="Translational Symmetry")
            #box.label(text="Point Reflection Symmetry")
            #box.label(text="Glide Reflection Symmetry")
        if props.edit_constraints=="connector":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
            row = box.row()
            row.prop(props, "conn_directions")
            col = row.column()
            col.operator("object.wfc_vis_directions", text="", icon="CUBE", depress=props.vis_directions)
            col.enabled = props.edit_type == 'objects'
            if props.conn_directions != '_NONE_':
                row = box.row()
                row.prop(props,"conn_name",text="Name")
                if len(get_known_conn_names(None, None)) > 1:
                    box.row().label(text="Known connector names:")
                    box.row().prop(props,"conn_known_names",text="")
                if not props.auto_save: box.row().operator("object.wfc_update_connector_constraints")
            if obj and not props.info_toggle:
                newbox = box.box()
                newbox.label(text=f"Defined connector constraints:")
                cf = newbox.column_flow(columns=2,align=True)
                c=0
                for d in DIRECTIONS:
                    pn = 'wfc_conn_' + d.lower()
                    if not pn in obj: continue
                    cf.label(text=f"{d.lower()}: {obj[pn]}")
                    c+=1
                if c==0: newbox.label(text="nothing defined yet")
        if props.edit_constraints == "dimensions":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
            box.row().prop(props, "dim_xyz")
            # if sum(props.dim_xyz)>3: box.row().prop(props, "dim_alignment")
            if not props.auto_save: box.operator("object.wfc_update_constraints")
        if props.edit_constraints == "fixed_position":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
            row = box.row()
            col = row.column()
            col.template_list("WFC3D_UL_FixedPositionList", "", props, "fixed_position_input_list", props, "fixed_position_input_list_idx")
            col = row.column()
            col.operator("object.wfc_generic_add_list_item", icon="ADD", text="")
            col.operator("object.wfc_generic_remove_list_items", icon="REMOVE", text="")
            if not props.auto_save: box.operator("object.wfc_update_constraints")
        if props.edit_constraints == "regfreq":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
            row = box.row()
            col = row.column()
            col.template_list("WFC3D_UL_RegFreqList","", props, "regfreq_input_list", props, "regfreq_input_list_idx")
            col = row.column()
            col.operator("object.wfc_generic_add_list_item", icon="ADD", text="")
            col.operator("object.wfc_generic_remove_list_items", icon="REMOVE", text="")
            if not props.auto_save: box.operator("object.wfc_update_constraints")
        if props.edit_constraints == "noise":
            box = box.box()
            row = box.row()
            row.label(text=obj_name)
            row.operator("object.wfc_reset_constraints")
            box.row().label(text="Noise on probability of occurrence:")
            box.row().prop(props, "noise_prob_basis")
            if props.noise_prob_basis != "_NONE_":
                box.row().prop(props, "noise_prob_threshold")
            box.row().label(text="Noise on transformations:")
            box.row().prop(props, "noise_transf_basis")
            if props.noise_transf_basis != "_NONE_":
                box.row().prop(props, "noise_transf_scale")
            if not props.auto_save: box.operator("object.wfc_update_constraints")

    def _draw_labels(self, layout, labels):
        for label in labels:
            layout.label(text=label)

    def draw_info_panel(self, layout, props, obj):
        box = layout.box()

        box.label(text="Constraints Information",icon="INFO_LARGE")

        labels = []
        for d in DIRECTIONS:
            pn = 'wfc_'+d.lower()
            if not pn in obj: continue
            labels.append(f"{d.lower()}: {obj[pn]}")
        if len(labels) > 0 or props.allow_neighbor_constraint_violations:
            sbox = box.box()
            sbox.label(text="Neighbor constraints")
            if len(labels) > 0: self._draw_labels(sbox.column_flow(columns=1, align=True), labels)
            if props.allow_neighbor_constraint_violations: sbox.prop(props, "allow_neighbor_constraint_violations", icon="VIEW_UNLOCKED")
            sbox.enabled = False

        labels = []
        for d in DIRECTIONS:
            pn = 'wfc_conn_'+d.lower()
            if not pn in obj: continue
            labels.append(f"{d.lower()}: {obj[pn]}")
        if len(labels) > 0:
            sbox = box.box()
            sbox.label(text="Connector constraints: ")
            self._draw_labels(sbox.column_flow(columns=3, align=True), labels)

        if sum(props.dim_xyz) > 3:
            row = box.box().row()
            row.enabled = False
            row.prop(props,"dim_xyz")

        self._draw_list_properties(props, box, "Fixed position constraints", FIXED_POSITION_CONSTRAINTS)

        labels = []
        for g in GRID_CONSTRAINTS:
            pn = 'wfc_' + g
            if not pn in obj: continue
            labels.append(f"{g}: {obj[pn]}")
        if len(labels) > 0:
            sbox = box.box()
            sbox.label(text="Grid constraints")
            self._draw_labels(sbox.column_flow(columns=2, align=True), labels)

        if sum(props.region_min) > -3 or sum(props.region_max) > -3 or sum(props.region_quadrant) < 8:
            sbox = box.box()
            sbox.label(text="Region constraints")
            if sum(props.region_min) > -3 or sum(props.region_max) > -3:
                row = sbox.row()
                row.enabled = False
                row.prop(props,"region_min")
                row = sbox.row()
                row.enabled = False
                row.prop(props,"region_max")
            row = sbox.row()
            if sum(props.region_quadrant) < 8:
                row.prop(props,"region_quadrant")
                row.enabled = False

        self._draw_properties(props, box, "Frequency constraints", FREQUENCY_CONSTRAINTS)
        self._draw_list_properties(props, box, "Region frequency constraints", REGFREQ_CONSTRAINTS)
        self._draw_properties(props, box, "Symmetry constraints", SYMMETRY_CONSTRAINTS)
        self._draw_properties(props, box, "Transformations", TRANSFORMATION_CONSTRAINTS)
        self._draw_properties(props, box, "Probability constraints", PROBABILITY_CONSTRAINTS)


    def _draw_list_properties(self, props, layout, name, constraints):
        p = constraints[0]
        lst = getattr(props, LIST_CONSTRAINTS[p])
        if len(lst) == 0: return
        box = layout.box()
        box.label(text=name)
        for i in range(len(lst)):
            for p in constraints:
                row = box.row()
                row.enabled = False
                row.prop(lst[i], p)

    def _draw_properties(self, props, layout, name, constraints):
        f = []
        for p in constraints:
            if p not in props: continue
            if cmpall(props[p], PROP_DEFAULTS[p]): continue
            f.append(p)
        if len(f) == 0: return
        box = layout.box()
        box.label(text=name)
        for p in f:
            row = box.row()
            row.enabled = False
            row.prop(props, p)

panels = [ WFC3D_UL_FixedPositionList, WFC3D_UL_RegFreqList, WFC3D_UL_EditPanelMultiSelList, WFC3D_UL_EditPanelNeighborMultiSelList, WFC3D_PT_EditPanel,]

        