import bpy
import numpy as np
from .objects import create_material, create_bar, create_cylinder, create_cone, create_pyramid, clone_and_scale_object, render_text_object, render_object
from .common import remap

def draw_2d_axes(target, props, data):
    cx,cy,cz = bpy.context.scene.cursor.location
    axis_mat = create_material(props.axes_color, roughness=props.axes_roughness, metallic=props.axes_metallic)
    axis = create_bar(axis_mat) if props.axes_shape == 'cube' else create_cylinder(axis_mat)
    arrow = create_pyramid(axis_mat) if props.axes_shape == 'cube' else create_cone(axis_mat)
    if props.axes_x:
        clone_and_scale_object(target, axis, (props.axes_thickness, props.axes_thickness, props.size[0]),(cx, cy, cz + props.axes_thickness/2), rot=(0, np.pi/2, 0))
        if props.axes_arrows:
            clone_and_scale_object(target, arrow, loc=(cx + props.size[0], cy, cz + props.axes_thickness/2), rot=(0, np.pi/2, 0), scale=(props.axes_thickness*2, props.axes_thickness*2, props.axes_thickness*2))
        if props.axes_labels:
            render_text_object(target["collection"], target["chart"], 'X', (cx + props.size[0], cy ,cz - props.spacing[2]), axis_mat, x_align="RIGHT", y_align="TOP", rot=(np.pi/2,0,0))
    if props.axes_y:
        clone_and_scale_object(target, axis, (props.axes_thickness, props.axes_thickness, props.size[1]),(cx, cy, cz + props.axes_thickness/2), rot=(-np.pi/2, 0, 0))
        if props.axes_arrows:
            clone_and_scale_object(target, arrow, loc=(cx, cy + props.size[1], cz + props.axes_thickness/2), rot=(-np.pi/2, 0, 0), scale=(props.axes_thickness*2, props.axes_thickness*2, props.axes_thickness*2))
        if props.axes_labels:
            render_text_object(target["collection"], target["chart"], 'Y', (cx - props.spacing[0], cy + props.size[1] ,cz), axis_mat, x_align="RIGHT", y_align="CENTER", rot=(np.pi/2,0,0))
    if props.axes_z:
        clone_and_scale_object(target, axis, (props.axes_thickness, props.axes_thickness, props.size[2]), (cx, cy, cz))
        if props.axes_arrows:
            clone_and_scale_object(target, arrow, loc=(cx, cy, cz + props.size[2]), scale=(props.axes_thickness*2, props.axes_thickness*2, props.axes_thickness*2))
        if props.axes_labels:
            render_text_object(target["collection"], target["chart"], 'Z', (cx - props.spacing[0] ,cy, cz + props.size[2]), axis_mat, x_align="RIGHT", y_align="TOP", rot=(np.pi/2,0,0))