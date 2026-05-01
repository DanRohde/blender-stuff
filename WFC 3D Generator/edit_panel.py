import bpy
from .helper import get_default_empty_object, get_icon_name, cmpall, get_selected_items, get_object_by_name, count_selected_items, get_active_constraints, render_source_collection
from .properties import get_known_conn_names
from .constants import *
import fnmatch
class WFC3DULGenericFilter:
    case_sensitive : bpy.props.BoolProperty(default=False, name="", description="Case sensitive", )
    def draw_filter(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "filter_name", text="", icon='VIEWZOOM')
        row.prop(self, "use_filter_invert", text="", icon='ARROW_LEFTRIGHT')
        row.prop(self, "case_sensitive", text="", icon="OUTLINER_OB_FONT")
    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item] * len(items)
        flt_neworder = []
        if self.filter_name and len(items) > 0:
            filterable_properties = [ p for p in items[0].keys() if isinstance(items[0][p], str) or isinstance(items[0][p], bpy.types.ID) ]
            for idx, item in enumerate(items):
                match = False
                for p in filterable_properties:
                    if p not in item: continue
                    name = item[p] if isinstance(item[p], str) else item[p].name
                    if not self.case_sensitive: name = name.lower()
                    match = match or self.filter_name in name or fnmatch.fnmatch(name, self.filter_name)
                flt_flags[idx] = self.bitflag_filter_item if match != self.use_filter_invert else 0
        return flt_flags, flt_neworder
class WFC3DULObjectFilter(WFC3DULGenericFilter):
    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item] * len(items)
        flt_neworder = []
        if self.filter_name:
            for idx, item in enumerate(items):
                name = item.obj.name if self.case_sensitive else item.obj.name.lower()
                filter_match = self.filter_name in name or fnmatch.fnmatch(name, self.filter_name)
                flt_flags[idx] = self.bitflag_filter_item if filter_match != self.use_filter_invert else 0
        return flt_flags, flt_neworder

class VIEW3D_UL_EditPanelMultiSelList(bpy.types.UIList, WFC3DULObjectFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        layout.row(align=True).prop(item, "selected", text=item.obj.name, icon=get_icon_name(item))

class VIEW3D_UL_EditPanelNeighborMultiSelList(bpy.types.UIList, WFC3DULObjectFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        layout.row(align=True).prop(item, "selected", text=item.obj.name, icon=get_icon_name(item))


class VIEW3D_UL_ConnectorExclusionList(bpy.types.UIList, WFC3DULGenericFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        row = layout.row(align=True)
        row.prop(item, "selected", text="")
        row.prop(item, "conn_excl_direction")
        row.prop(item, "conn_excl_name", placeholder="Connector name")

class VIEW3D_UL_MultipleConnectorList(bpy.types.UIList, WFC3DULGenericFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        row = layout.row(align=True)
        row.prop(item, "selected", text="")
        row.prop(item, "mult_conn_direction")
        row.prop(item, "mult_conn_name", placeholder="Connector name")


class VIEW3D_UL_RegFreqList(bpy.types.UIList, WFC3DULGenericFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        row = layout.row(align=True)
        col = row.column(align=True)
        row = col.row(align=True)
        row.column(align=True).prop(item,"selected", text=f"{index}.")
        row.column(align=True).prop(item,"regfreq_name", text="", placeholder="Optional region name")
        col.row().prop(item,"regfreq_min")
        col.row().prop(item,"regfreq_max")
        row = col.row(align=True)
        row.prop(item,"regfreq_freq")
        row.prop(item,"regfreq_freq_pct")
        row = col.row()
        row.separator()

class VIEW3D_UL_FixedPositionList(bpy.types.UIList, WFC3DULGenericFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        row = layout.row(align=True)
        row.prop(item,"selected", text="")
        row.prop(item,"fixed_position_type")
        if item.fixed_position_type == 'absolute':
            row.prop(item,"fixed_position_xyz")
        else:
            row.prop(item,"fixed_position_pct")

class VIEW3D_UL_RegProbList(bpy.types.UIList, WFC3DULGenericFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        row = layout.row(align=True)
        col = row.column(align=True)
        row = col.row(align=True)
        row.alignment = 'LEFT'
        row.column(align=True).prop(item, "selected", text=f"{index}.")
        row.column(align=True).prop(item,"regprob_name", text="", placeholder="Optional region name")
        col.row(align=True).prop(item,"regprob_min")
        col.row(align=True).prop(item,"regprob_max")
        row = col.row(align=True)
        row.prop(item, "regprob_probability")
        row.prop(item, "regprob_weight")
        row = col.row()
        row.separator()

class VIEW3D_UL_DistanceList(bpy.types.UIList, WFC3DULGenericFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        row = layout.row(align=True)
        ocol = row.column(align=True)
        ocol.row(align=True).prop(item, "selected", text=f"{index}.")
        col = ocol.column(align=True)
        col.row(align=True).prop(item, "distance")
        col.prop(item, "distance_from")
        if item.distance_from == 'object':
            col.prop(item, "distance_object")
        elif item.distance_from == 'position':
            row = col.row(align=True)
            row.prop(item, "distance_position_type")
            if item.distance_position_type == 'absolute':
                row.prop(item, "distance_position",text="")
            else:
                row.prop(item, "distance_position_pct")
        else:
            col.row(align=True).prop(item, "distance_subcollection")
        col.prop(item, "distance_type")
        row = ocol.row()
        row.separator()
class VIEW3D_UL_ActiveConstraintsList(bpy.types.UIList, WFC3DULGenericFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        layout.row(align=True).prop(item, "selected", text=item.constraint, icon="SETTINGS")

def draw_empty_neighbor_list_item(layout, item):
    row = layout.row(align=True)
    direction = item.direction.split('_')
    row.prop(item, "selected", text=f"{DIR_TRANSLATION[direction[0] if len(direction) == 1 else direction[1]]}", icon="VIEW_LOCKED" if item.selected else "VIEW_UNLOCKED")

class VIEW3D_UL_EmptyNeighborList(bpy.types.UIList, WFC3DULGenericFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        draw_empty_neighbor_list_item(layout, item)
class VIEW3D_UL_EmptyAnyNeighborList(bpy.types.UIList, WFC3DULGenericFilter):
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        draw_empty_neighbor_list_item(layout, item)

class VIEW3D_PT_EditPanel(bpy.types.Panel):
    """User interface for WFC 3D Constraints Editor"""
    bl_label = "WFC 3D Constraints Editor"
    bl_idname = "VIEW3D_PT_wfc_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WFC 3D Edit'

    def draw(self, context):
        layout = self.layout
        props = context.scene.wfc_props
        render_source_collection(context, layout)
        col = layout.column(align=True)
        if not props.collection_obj:
            layout.label(text="Choose a Source Collection", icon='INFO')
            return
        
        if len(props.obj_list) == 0:
            layout.label(text="Empty Collection")
            return
            
        box = col.box()
        box.prop(props,"edit_type", icon="OBJECT_DATA")

        if props.edit_type == 'constraints':
            box = layout.box()
            row = box.row(align=True)
            col = row.column(align=True)
            col.template_list("VIEW3D_UL_ActiveConstraintsList","", props, "active_constraints_input_list", props, "active_constraints_input_list_idx",rows=18, maxrows=18)
            col = row.box().column(align=True)
            col.operator('object.wfc_auto_save_toggle', icon='IMPORT', depress=props.auto_save)
            col.separator()
            draw_list_selection_actions(props, col,"active_constraints_input_list")
            box.prop(props, "show_inactive_constraints_menu_items")
            if not props.auto_save: box.operator("object.wfc_save_active_constraints", icon='IMPORT')
            return

        if props.edit_type == 'reset':
            box = layout.box()

            box.prop(props, "reset_all_confirmation")
            row = box.row()
            row.operator("object.wfc_reset_all_constraints").sure = props.reset_all_confirmation
            row.enabled = props.reset_all_confirmation
            return

        selected = []
        if props.edit_type == 'objects':
            sel_count = count_selected_items(props.obj_list)
            newrow = box.row()
            nc=newrow.column().box()
            nc.operator("object.wfc_get_selected_object", icon="SELECT_SET").list_name="obj_list"
            nc.prop(props,"auto_active_object", icon="TRIA_RIGHT")
            nc.operator("object.wfc_update_collection_list", icon="FILE_REFRESH")
            nc=newrow.column()
            nc.template_list("VIEW3D_UL_EditPanelMultiSelList","", props, "obj_list", props, "obj_list_idx")
            nc.enabled = not props.auto_active_object
            nc=newrow.column().box()
            c = nc.column()
            c.operator("object.wfc_select_dropdown_object", icon='RESTRICT_SELECT_OFF').list_name="obj_list"
            c.enabled = sel_count > 0
            draw_list_selection_actions(props, nc, "obj_list")

        
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

        row = box.box().row(align=True)
        row.operator('object.wfc_info_toggle',icon='INFO_LARGE', depress = props.info_toggle)
        row.prop(props,"edit_constraints",icon="SETTINGS")
        row.operator("object.wfc_open_web_link", icon="URL", text="").url = HELP["constraints"]["url"] + "#" + HELP["constraints"]["anchormap"][props.edit_constraints]
        row.operator('object.wfc_auto_save_toggle',icon='IMPORT',depress = props.auto_save)

        if hasattr(self, f"draw_{props.edit_constraints}_panel") and callable(getattr(self, f"draw_{props.edit_constraints}_panel")):
            if props.edit_constraints not in get_active_constraints():
                box.label(text="These constraints are disabled.", icon="INFO_LARGE")
                box = box.box()
                box.enabled = False
            draw_method = getattr(self, f"draw_{props.edit_constraints}_panel")
            draw_method(props, box, obj, obj_name)

        if props.info_toggle: self.draw_info_panel(layout, props, obj)
        row = layout.box().row()
        row.alignment = "LEFT"
        if props.edit_constraints != '_none_':
            row.prop(props, "copy_constraints")
        else:
            row.label(text="Copy all constraints from")
        row.prop(props, "copy_from")
        row.prop(props, "copy_overwrite")
        col = row.column()
        col.operator("object.wfc_copy_constraints_from_object", icon="COPYDOWN")
        col.enabled = props.copy_from is not None
        if props.edit_constraints != "":
            row = layout.row()
            row.operator("object.wfc_open_web_link", icon="URL", text="Visit GitHub to get help").url = HELP["constraints"]["url"]+"#"+HELP["constraints"]["anchormap"][props.edit_constraints]
    def draw_neighbor_panel(self, props, layout, obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints", text="Reset")
        row = box.row()
        row.prop(props, "edit_neighbor_constraint")
        col = row.column()
        col.operator("object.wfc_vis_directions", text="", icon="CUBE", depress=props.vis_directions)
        col.enabled = props.edit_type == 'objects'


        if props.edit_neighbor_constraint and props.edit_neighbor_constraint != "_NONE_":
            box.prop(props, "no_neighbor_allowed", icon="VIEW_LOCKED")
            row = box.row()
            row.enabled = not props.no_neighbor_allowed
            newcol = row.column().box()
            newcol.operator("object.wfc_get_selected_object", icon="SELECT_SET").list_name = "neighbor_list"
            nc = newcol.column()
            nc.prop(props, "auto_neighbor_object", icon="TRIA_RIGHT")
            nc.enabled = not props.auto_active_object
            newcol.operator("object.wfc_update_collection_list", icon="FILE_REFRESH")
            newcol = row.column()
            newcol.template_list("VIEW3D_UL_EditPanelNeighborMultiSelList", "", props, "neighbor_list", props, "neighbor_list_idx")
            newcol.enabled = not props.auto_neighbor_object
            newcol = row.column().box()
            newcol.enabled = not props.auto_neighbor_object
            sel_count = count_selected_items(props.neighbor_list)
            nr = newcol.row()
            nr.operator("object.wfc_select_dropdown_object", icon='RESTRICT_SELECT_OFF').list_name = "neighbor_list"
            nr.enabled = not props.auto_active_object and sel_count > 0
            draw_list_selection_actions(props, newcol, "neighbor_list")

            box.row().prop(props, "allow_neighbor_constraint_violations", icon="VIEW_UNLOCKED")

            if not props.auto_save: box.row().operator("object.wfc_update_neighbor_constraints", icon='IMPORT')
        if obj and not props.info_toggle:
            newbox = box.box()
            newbox.label(text=f"Defined neighbor constraints:")
            c = 0
            for d in DIRECTIONS:
                if 'wfc_' + d.lower() not in obj: continue
                c += 1
                newbox.label(text=f"{DIR_TRANSLATION[d]}: {obj['wfc_' + d.lower()]}")
            if c == 0: newbox.label(text="nothing defined yet")
    def draw_grid_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")
        newbox = box.box()
        newrow = newbox.row()
        newrow.label(text="Corners")
        newrow.prop(props, "corner_none")
        if not props.corner_none:
            row = newbox.row()
            for c in ['fbl', 'fbr', 'ftl', 'ftr']:
                row.prop(props, "corner_" + c)

            row = newbox.row()
            for c in ['bbl', 'bbr', 'btl', 'btr']:
                row.prop(props, "corner_" + c)

        newbox = box.box()
        newrow = newbox.row()
        newrow.label(text="Edges")
        newrow.prop(props, "edge_none")
        if not props.edge_none:
            for p in ['f', 'b']:
                row = newbox.row()
                for c in ['b', 'l', 't', 'r']:
                    row.prop(props, "edge_" + p + c)
            row = newbox.row()
            for p in ['lb', 'lt', 'rb', 'rt']:
                row.prop(props, "edge_" + p)

        newbox = box.box()
        newrow = newbox.row()
        newrow.label(text="Faces")
        newrow.prop(props, "face_none")
        if not props.face_none:
            row = newbox.row()
            for f in ['front', 'left', 'top']:
                row.prop(props, "face_" + f)
            row = newbox.row()
            for f in ['back', 'right', 'bottom']:
                row.prop(props, "face_" + f)

        newbox = box.box()
        newrow = newbox.row()
        newrow.label(text="Inside")
        newrow.prop(props, "inside_none")

        if not props.auto_save: box.operator("object.wfc_update_grid_constraints", icon='IMPORT')
    def draw_region_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")
        row = box.row()
        row.prop(props, "region_min")
        row = box.row()
        row.prop(props, "region_max")

        row = box.row()
        row.label(text="Quadrant:")
        row.prop(props, "region_quadrant", text="")
        ql = ", ".join([l for q, l in zip(props.region_quadrant, ['fbl', 'fbr', 'ftl', 'ftr', 'bbl', 'bbr', 'btl', 'btr']) if q])
        box.row().label(text=f"Selected quadrant: {ql}")

        row = box.row()
        row.label(text="Level:")
        row = row.column_flow(columns=3, align=True)
        row.prop(props, "region_level_ground")
        row.prop(props, "region_level_first")
        row.prop(props, "region_level_second")
        row.prop(props, "region_level_mid")
        row.prop(props, "region_level_penultimate")
        row.prop(props, "region_level_top")

        if not props.auto_save: box.operator("object.wfc_update_constraints", icon='IMPORT')
    def draw_probability_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")
        box.prop(props, "probability")
        box.prop(props, "weight")
        box.prop(props, "auto_weight", icon="MOD_VERTEX_WEIGHT")

        if not props.auto_save: box.operator("object.wfc_update_constraints", icon='IMPORT')
    def draw_transformations_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")
        newbox = box.box()
        newbox.label(text="Translation Offset")
        newbox.row().prop(props, "translation_min")
        newbox.row().prop(props, "translation_max")
        newbox.row().prop(props, "translation_steps")

        newbox = box.box()
        newbox.label(text="Rotation")
        newbox.row().prop(props, "rotation_min")
        newbox.row().prop(props, "rotation_max")
        newbox.row().prop(props, "rotation_steps")

        newbox = box.box()
        newrow = newbox.row()
        newrow.label(text="Scale")
        newrow.prop(props, "scale_type")
        if props.scale_type == 'uniform':
            newbox.prop(props, "scale_uni")
        elif props.scale_type == 'non-uniform':
            newbox.row().prop(props, "scale_min")
            newbox.row().prop(props, "scale_max")
            newbox.row().prop(props, "scale_steps")

        newbox = box.box()
        newrow = newbox.row()
        newrow.prop(props, "flipping")
        if not props.auto_save: box.operator('object.wfc_update_constraints', icon='IMPORT')
    def draw_frequency_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")

        newbox = box.box()
        newbox.label(text="Same Object")
        row = newbox.row()
        row.prop(props, "freq_grid")
        row.prop(props, "freq_grid_pct")
        newbox.prop(props, "freq_neighbor")
        newbox.prop(props, "freq_neighbor_face")
        newbox.prop(props, "freq_neighbor_corner")
        newbox.prop(props, "freq_neighbor_edge")
        row = newbox.row()
        row.prop(props, "freq_axes")

        newbox = box.box()
        newbox.label(text="Any Object")
        newbox.prop(props, "freq_any_neighbor")
        newbox.prop(props, "freq_any_neighbor_face")
        newbox.prop(props, "freq_any_neighbor_corner")
        newbox.prop(props, "freq_any_neighbor_edge")

        row = newbox.row()
        row.prop(props, "freq_any_axes")

        if not props.auto_save: box.operator("object.wfc_update_constraints", icon='IMPORT')

    def draw_symmetry_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")

        box.label(text="Mirror Symmetry")
        newbox = box.box()
        newbox.row().prop(props, "sym_mirror_axes")
        if props.edit_type == 'objects':
            if props.sym_mirror_axes[0]: newbox.prop(props, "sym_mirror_axes_x", text="X Partner")
            if props.sym_mirror_axes[1]: newbox.prop(props, "sym_mirror_axes_y", text="Y Partner")
            if props.sym_mirror_axes[2]: newbox.prop(props, "sym_mirror_axes_z", text="Z Partner")
            if props.sym_mirror_axes[0] and props.sym_mirror_axes[1]: newbox.prop(props, "sym_mirror_axes_xy", text="XY Partner")
            if props.sym_mirror_axes[0] and props.sym_mirror_axes[2]: newbox.prop(props, "sym_mirror_axes_xz", text="XZ Partner")
            if props.sym_mirror_axes[1] and props.sym_mirror_axes[2]: newbox.prop(props, "sym_mirror_axes_yz", text="YZ Partner")
            if props.sym_mirror_axes[0] and props.sym_mirror_axes[1] and props.sym_mirror_axes[2]: newbox.prop(props, "sym_mirror_axes_xyz", text="XYZ Partner")

        if sum(props['sym_mirror_axes']) > 0:
            newbox.row().label(text="Flip Mirror Partner")
            fmpbox = newbox.box()
            row = fmpbox.column_flow(columns=4, align=True)
            if props.sym_mirror_axes[0]: row.prop(props, "sym_mirror_flip_x")
            if props.sym_mirror_axes[1]: row.prop(props, "sym_mirror_flip_y")
            if props.sym_mirror_axes[2]: row.prop(props, "sym_mirror_flip_z")
            if props.sym_mirror_axes[0] and props.sym_mirror_axes[1]: row.prop(props, "sym_mirror_flip_xy")
            if props.sym_mirror_axes[0] and props.sym_mirror_axes[2]: row.prop(props, "sym_mirror_flip_xz")
            if props.sym_mirror_axes[1] and props.sym_mirror_axes[2]: row.prop(props, "sym_mirror_flip_yz")
            if props.sym_mirror_axes[0] and props.sym_mirror_axes[1] and props.sym_mirror_axes[2]: row.prop(props, "sym_mirror_flip_xyz")

            flip = sum([props['sym_mirror_flip_' + k] for k in ['x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz']])
            if flip > 0: fmpbox.row().prop(props, "sym_mirror_flip_transl")

            newbox.row().prop(props, "sym_mirror_trans")

        box.label(text="Rotational Symmetry")
        newbox = box.box()
        newbox.row().prop(props, "sym_rotate_axis")
        newbox.prop(props, "sym_rotate_n")

        if not props.auto_save: box.operator("object.wfc_update_constraints", icon='IMPORT')

    def draw_connector_panel(self, props, layout, obj, obj_name):
        box = layout.box()
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
            row.prop(props, "conn_name", text="", placeholder="Connector name")
            if len(get_known_conn_names(None, None)) > 1:
                box.row().label(text="Known connector names:")
                box.row().prop(props, "conn_known_names", text="")
            if not props.auto_save: box.row().operator("object.wfc_update_connector_constraints", icon='IMPORT')

        if obj and not props.info_toggle:
            newbox = box.box()
            newbox.label(text=f"Defined connector constraints:")
            cf = newbox.column_flow(columns=2, align=True)
            c = 0
            for d in DIRECTIONS:
                pn = 'wfc_conn_' + d.lower()
                if not pn in obj: continue
                cf.label(text=f"{d.lower()}: {obj[pn]}")
                c += 1
            if c == 0: newbox.label(text="nothing defined yet")
    def draw_dimensions_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")
        box.row().prop(props, "dim_xyz")
        if not props.auto_save: box.operator("object.wfc_update_constraints", icon='IMPORT')

    def draw_fixed_position_panel(self, props, layout, obj, obj_name):
        self._draw_list_constraints_panel(props, layout, obj, obj_name,"VIEW3D_UL_FixedPositionList","fixed_position_input_list")

    def draw_regfreq_panel(self, props, layout, obj, obj_name):
        self._draw_list_constraints_panel(props, layout, obj, obj_name,"VIEW3D_UL_RegFreqList","regfreq_input_list")

    def draw_noise_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")
        box.row().label(text="Noise on probability of occurrence:")
        box.row().prop(props, "noise_prob_basis")
        if props.noise_prob_basis != "_NONE_":
            box.row().prop(props, "noise_prob_threshold")
            box.row().prop(props, "noise_prob_scale")
        box.row().label(text="Noise on transformations:")
        box.row().prop(props, "noise_transf_basis")
        if props.noise_transf_basis != "_NONE_":
            box.row().prop(props, "noise_transf_scale")

        box.row().prop(props, "noise_randomize_position")
        if not props.auto_save: box.operator("object.wfc_update_constraints", icon='IMPORT')

    def draw_geometry_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")

        box.row().label(text="Applies only to mesh objects.", icon="INFO_LARGE")
        row = box.row()
        row.label(text="Match")
        row.prop(props, "geo_match_edges")
        row.prop(props, "geo_match_faces")

        row = box.row()
        row.enabled = props.geo_match_edges or props.geo_match_faces
        row.column().label(text="Faces:")
        col = row.column()
        for i, d in enumerate(FACE_DIRECTIONS):
            if i !=0 and i % 2 == 0: col = row.column()
            col.prop(props, f"geo_{d.lower()}")
        row = box.row()
        row.enabled = props.geo_match_edges or props.geo_match_faces
        row.prop(props, "geo_tolerance")
        row.prop(props, "geo_threshold")
        if not props.auto_save: box.operator("object.wfc_update_constraints", icon='IMPORT')

    def draw_regprob_panel(self, props, layout, obj, obj_name):
        self._draw_list_constraints_panel(props, layout, obj, obj_name,"VIEW3D_UL_RegProbList","regprob_input_list")

    def draw_distance_panel(self, props, layout, obj, obj_name):
        self._draw_list_constraints_panel(props, layout, obj, obj_name,"VIEW3D_UL_DistanceList","distance_input_list")

    def draw_connector_exclusion_panel(self, props, layout, obj, obj_name):
        self._draw_list_constraints_panel(props, layout, obj, obj_name,"VIEW3D_UL_ConnectorExclusionList","conn_excl_input_list")

    def draw_multiple_connector_panel(self, props, layout, obj, obj_name):
        self._draw_list_constraints_panel(props, layout, obj, obj_name, "VIEW3D_UL_MultipleConnectorList", "mult_conn_input_list")

    def draw_empty_panel(self, props, layout, _obj, obj_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")
        nbox = box.box()
        row = nbox.row()
        row.label(text="Prohibit empty neighbors in selected directions:")
        row = nbox.row()
        col = row.column()
        col.template_list("VIEW3D_UL_EmptyNeighborList", "", props, "empty_neighbor_list", props, "empty_neighbor_list_idx")
        col = row.column().box()
        nc = col.column()
        nc.operator("object.wfc_vis_directions", text="", icon="CUBE", depress=props.vis_directions)
        nc.enabled = props.edit_type == 'objects'
        draw_list_selection_actions(props, col, "empty_neighbor_list")

        sl = [item.direction.lower() for item in props.empty_neighbor_list if item.selected]
        if len(sl) > 0: nbox.row().label(text=f"Selected direction(s): " + ", ".join(sl))
        nbox = box.box()
        row = nbox.row()
        row.label(text="Prohibit any empty neighbors in selected directions:")
        row = nbox.row()
        col = row.column()
        col.template_list("VIEW3D_UL_EmptyAnyNeighborList", "", props, "empty_any_neighbor_list", props, "empty_any_neighbor_list_idx")
        col = row.column().box()
        nc = col.column()
        nc.operator("object.wfc_vis_directions", text="", icon="CUBE", depress=props.vis_directions)
        nc.enabled = props.edit_type == 'objects'
        draw_list_selection_actions(props, col, "empty_any_neighbor_list")
        sl = [item.direction.lower() for item in props.empty_any_neighbor_list if item.selected]
        if len(sl) > 0: nbox.row().label(text=f"Selected direction(s): " + ", ".join(sl))

        if not props.auto_save: box.operator("object.wfc_update_constraints", icon='IMPORT')

    def _draw_list_constraints_panel(self, props, layout, _obj, obj_name, ui_list, list_name):
        box = layout.box()
        row = box.row()
        row.label(text=obj_name)
        row.operator("object.wfc_reset_constraints")
        row = box.row()
        col = row.column()
        col.template_list(ui_list, "", props, list_name, props, f"{list_name}_idx", sort_lock = True)
        draw_list_order_actions(props, col, list_name)
        self._draw_list_modify_actions(props, row.box().column(), list_name)
        if not props.auto_save: box.operator("object.wfc_update_constraints", icon='IMPORT')

    def _draw_list_modify_actions(self, props, col, list_name):
        col.operator("object.wfc_generic_add_list_item", icon="ADD", text="").list_name = list_name
        c = col.column()
        c.operator("object.wfc_generic_remove_list_items", icon="REMOVE", text="").list_name = list_name
        c.operator("object.wfc_generic_duplicate_selected_items", icon="DUPLICATE", text="").list_name = list_name
        c.enabled = count_selected_items(getattr(props, list_name)) > 0
        col.separator()
        draw_list_selection_actions(props, col, list_name)

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
        self._draw_list_properties(props, box, "Connector exclusion constraints", CONNECTOR_EXCLUSION_CONSTRAINTS)
        self._draw_list_properties(props, box, "Multiple connector constraints", MULTIPLE_CONNECTOR_CONSTRAINTS)
        self._draw_properties(props, box, "Geometry constraints", GEOMETRY_CONSTRAINTS)

        self._draw_selection_properties(props, box, "Empty neighbor constraints", EMPTY_NEIGHBOR_CONSTRAINTS)

        self._draw_properties(props, box, "Dimensions constraints", DIMENSIONS_CONSTRAINTS)

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

        self._draw_list_properties(props, box, "Distance constraints", DISTANCE_CONSTRAINTS)

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
        self._draw_list_properties(props, box, "Region probability constraints", REGPROB_CONSTRAINTS)


    def _draw_list_properties(self, props, layout, name, constraints):
        lst = getattr(props, LIST_CONSTRAINTS[constraints[0]])
        if len(lst) == 0: return
        box = layout.box()
        box.label(text=name)
        for i in range(len(lst)):
            for j in range(len(constraints)):
                row = box.row()
                row.enabled = False
                if j == 0: row.label(text=f"{i}.")
                row.prop(lst[i], constraints[j])

    def _draw_selection_properties(self, props, layout, name, constraints):
        result = {}
        render = False
        for c in constraints:
            result[c] = []
            lst = getattr(props, SELECTION_CONSTRAINTS[c])
            result[c] = [item for item in lst if item.selected]
            render = render or len(result[c]) > 0

        if not render: return
        box = layout.box()
        box.label(text=name)
        for r in result:
            if len(result[r]) == 0: continue
            row = box.row()
            row.enabled = False
            row.label(text=f"{r}")
            for item in result[r]:
                for k in item.keys():
                    if k != "selected": row.prop(item, k, text="")
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
def draw_list_selection_actions(props, column, list_name):
    lst = getattr(props, list_name)
    nc = column.column()
    nc.operator("object.wfc_list_select_all", icon="CHECKBOX_HLT", text="").list_name = list_name
    nc.enabled = len(lst) > 0
    nc = column.column()
    nc.operator("object.wfc_list_select_none", icon="CHECKBOX_DEHLT", text="").list_name = list_name
    nc.enabled = count_selected_items(lst) > 0
    nc = column.column()
    nc.operator("object.wfc_list_invert_selection", icon="CHECKMARK", text="").list_name = list_name
    nc.enabled = len(lst) > 0

def draw_list_order_actions(props, column, list_name, call_auto_save = True):
    lst = getattr(props, list_name)
    row = column.box().row()
    row.enabled = len(lst) > 1 and count_selected_items(lst) > 0
    op = row.operator("object.wfc_generic_order_up", icon="TRIA_UP")
    op.list_name = list_name
    op.call_auto_save = call_auto_save
    op = row.operator("object.wfc_generic_order_down", icon="TRIA_DOWN")
    op.list_name = list_name
    op.call_auto_save = call_auto_save

panels = [ VIEW3D_UL_ActiveConstraintsList, VIEW3D_UL_MultipleConnectorList, VIEW3D_UL_ConnectorExclusionList, VIEW3D_UL_EmptyNeighborList, VIEW3D_UL_EmptyAnyNeighborList, VIEW3D_UL_DistanceList, VIEW3D_UL_RegProbList, VIEW3D_UL_FixedPositionList,\
           VIEW3D_UL_RegFreqList, VIEW3D_UL_EditPanelMultiSelList, VIEW3D_UL_EditPanelNeighborMultiSelList, VIEW3D_PT_EditPanel,]

        