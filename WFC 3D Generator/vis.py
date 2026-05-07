import bpy
from .constants import *
import numpy as np

def _create_and_link(ng, loc, node_type, input_sockets, output_sockets={}, attr={}):
    loc[0] += loc[2]
    loc[1] += loc[3]
    nn = ng.nodes.new(node_type)
    for a, v in attr.items():
        if hasattr(nn, a): setattr(nn, a, v)
    nn.location = (loc[0], loc[1])
    for input_socket_name, s in input_sockets.items():
        ng.links.new(s, nn.inputs[input_socket_name])
    for output_socket_name, s in output_sockets.items():
        ng.links.new(nn.outputs[output_socket_name], s)
    return nn, loc

def _create_direction_text_nodes(ng, loc, ig, dirname, dirvec, jg, vmin, vmax):

    stc, loc = _create_and_link(ng, loc, 'GeometryNodeStringToCurves', {'Size': ig.outputs['Text Size']})
    if "_" in dirname: dirname = dirname.split("_")[1]
    stc.inputs[0].default_value = dirname.lower()
    stc.inputs[1].default_value = 1
    if hasattr(stc, "align_x"): 
        align_x = { -1: 'RIGHT', 0 : 'CENTER', 1 : 'LEFT'}
        stc.align_x = align_x[dirvec[0]]
    else:
        align_x = { -1: 'Right', 0 : 'Center', 1 : 'Left'}
        stc.inputs[3].default_value = align_x[dirvec[0]]
    if hasattr(stc, "align_y"):
        align_y = { -1: 'TOP', 0: 'MIDDLE', 1: 'BOTTOM'}
        stc.align_y = align_y[dirvec[1]]
    else:
        align_y = { -1: 'Top', 0: 'Middle', 1: 'Bottom'}
        stc.inputs[4].default_value = align_y[dirvec[1]]

    sp, loc = _create_and_link(ng, loc, 'GeometryNodeSetPosition', {'Geometry':stc.outputs[0]},{0:jg.inputs[0]})
    input_sockets = {}
    axis=['X', 'Y', 'Z']
    for i in range(3):
        if dirvec[i] == 0: continue
        if dirvec[i] < 0: input_sockets[axis[i]] = vmin.outputs[axis[i]]
        if dirvec[i] > 0: input_sockets[axis[i]] = vmax.outputs[axis[i]]
    cxyz, loc = _create_and_link(ng, loc, 'ShaderNodeCombineXYZ', input_sockets, {'Vector':sp.inputs['Offset']})

    return loc

def _get_directions_geometry_nodegroup(gn):
    if gn in bpy.data.node_groups:
        nodegroup = bpy.data.node_groups[gn]
        if nodegroup.bl_idname == 'GeometryNodeTree': return nodegroup

    ng = bpy.data.node_groups.new(gn, 'GeometryNodeTree')
    # clean up
    #while ng.nodes: ng.nodes.remove(ng.nodes[0])
    #while ng.interface.items_tree: ng.interface.remove(ng.interface.items_tree[0])

    nodes = ng.nodes
    # Group Input and Group Output inclusive Sockets
    ig = nodes.new('NodeGroupInput')
    ig.location = (0,0)
    og = nodes.new('NodeGroupOutput')
    og.location = (1000, 0)
    input_sockets = [ {'name': 'Geometry', 'socket_type': 'NodeSocketGeometry' },
                      {'name': 'Text Size', 'socket_type': 'NodeSocketFloat', 'attr': { 'min_value': 0, 'default_value': .5, 'subtype': 'DISTANCE'}},
                      {'name': 'Text Rotation', 'socket_type': 'NodeSocketFloat', 'attr': { 'min_value': 0, 'max_value': np.pi*2 , 'default_value': np.pi/2}, 'subtype': 'ANGLE'},
                      {'name': 'Hide Object', 'socket_type': 'NodeSocketBool'},
                      {'name': 'Hide Bounding Box', 'socket_type': 'NodeSocketBool'},
                      {'name': 'Hide Face Names', 'socket_type': 'NodeSocketBool'},
                      {'name': 'Hide Corner Names', 'socket_type': 'NodeSocketBool'},
                      {'name': 'Hide Edge Names', 'socket_type': 'NodeSocketBool'},
                      {'name': 'Radius', 'socket_type': 'NodeSocketFloat', 'attr': {'min_value': 0, 'default_value': 0.01, 'subtype': 'DISTANCE'}},
                      {'name': 'Resolution', 'socket_type': 'NodeSocketInt', 'attr': {'min_value': 3, 'default_value': 3}},
    ]
    for in_sockets in input_sockets:
        ng.interface.new_socket(name=in_sockets['name'], in_out='INPUT', socket_type=in_sockets['socket_type'])
        if 'attr' in in_sockets:
            for a, v in in_sockets['attr'].items():
                setattr(ng.interface.items_tree[in_sockets['name']], a, v)
    ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')

    loc = [1000,0,-200,0]
    # Original Object to Curve -> Switch -> Join Geometry -> Output
    #jg, loc = _create_and_link(ng, loc, 'GeometryNodeJoinGeometry',{},{'Geometry':og.inputs['Geometry']})
    jg, loc = _create_and_link(ng, loc, 'GeometryNodeJoinGeometry', {})
    ctm, loc = _create_and_link(ng, loc, 'GeometryNodeCurveToMesh', {'Curve': jg.outputs['Geometry']}, {'Mesh': og.inputs['Geometry']})
    cc, loc = _create_and_link(ng, loc, 'GeometryNodeCurvePrimitiveCircle', {'Radius': ig.outputs['Radius'], 'Resolution': ig.outputs['Resolution']}, {'Curve': ctm.inputs['Profile Curve']}, {'mode':'RADIUS'})
    nsw, loc = _create_and_link(ng, loc, 'GeometryNodeSwitch', {'Switch':ig.outputs['Hide Object']},{'Output':jg.inputs['Geometry']}, {'input_type':'GEOMETRY'})
    _m2c,_loc = _create_and_link(ng, loc, 'GeometryNodeMeshToCurve', {  'Mesh' : ig.outputs['Geometry']}, { 'Curve' : nsw.inputs['False']})

    loc = [800,200,-200,0]
    nsw, loc = _create_and_link(ng, loc, 'GeometryNodeSwitch', {'Switch': ig.outputs['Hide Bounding Box']}, {'Output':jg.inputs['Geometry']}, {'input_type':'GEOMETRY'})
    m2c, loc = _create_and_link(ng, loc, 'GeometryNodeMeshToCurve', {},{'Curve': nsw.inputs['False']})
    bb, loc = _create_and_link(ng, loc, 'GeometryNodeBoundBox', {'Geometry': ig.outputs['Geometry']}, {'Bounding Box': m2c.inputs['Mesh']})

    loc = [400,200,0,200]
    vmin, loc = _create_and_link(ng, loc, 'ShaderNodeSeparateXYZ', {'Vector' : bb.outputs['Min']})
    vmax, loc = _create_and_link(ng, loc, 'ShaderNodeSeparateXYZ', {'Vector' : bb.outputs['Max']})



    jtn, loc = _create_and_link(ng, loc, 'GeometryNodeJoinGeometry', {})
    cxyz, loc = _create_and_link(ng, loc, 'ShaderNodeCombineXYZ',{'X':ig.outputs['Text Rotation']})
    ri, loc = _create_and_link(ng, loc, 'GeometryNodeRotateInstances',{'Instances' : jtn.outputs[0],'Rotation':cxyz.outputs['Vector']})
    _create_and_link(ng, loc, 'GeometryNodeRealizeInstances', {'Geometry' : ri.outputs[0]}, {0:jg.inputs[0]})



    loc = [400,400,200,0]
    nsw, loc = _create_and_link(ng, loc, 'GeometryNodeSwitch',{'Switch':ig.outputs['Hide Face Names']}, {'Output':jtn.inputs[0]}, {'input_type':'GEOMETRY'})
    jgd, loc = _create_and_link(ng, loc, 'GeometryNodeJoinGeometry', {}, {0:nsw.inputs['False']})

    for dirname, dirvec in FACE_DIRECTIONS.items():
        loc = _create_direction_text_nodes(ng, loc, ig, dirname, dirvec, jgd, vmin, vmax)

    loc = [400,700,200,0]
    nsw, loc = _create_and_link(ng, loc, 'GeometryNodeSwitch',{'Switch':ig.outputs['Hide Edge Names']}, {'Output':jtn.inputs[0]}, {'input_type':'GEOMETRY'})
    jgd, loc = _create_and_link(ng, loc, 'GeometryNodeJoinGeometry', {}, {0:nsw.inputs['False']})

    for dirname, dirvec in EDGE_DIRECTIONS.items():
        loc = _create_direction_text_nodes(ng, loc, ig, dirname, dirvec, jgd, vmin, vmax)

    loc = [400,1000,200,0]
    nsw, loc = _create_and_link(ng, loc, 'GeometryNodeSwitch', {'Switch': ig.outputs['Hide Corner Names']},{'Output': jtn.inputs[0]}, {'input_type':'GEOMETRY'})
    jgd, loc = _create_and_link(ng, loc, 'GeometryNodeJoinGeometry', {}, {0: nsw.inputs['False']})

    for dirname, dirvec in CORNER_DIRECTIONS.items():
        loc = _create_direction_text_nodes(ng, loc, ig, dirname, dirvec, jgd, vmin, vmax)

    ng.nodes.update()
    return ng



def add_directions_geometry_nodegroup(obj):
    ngn = NODEGROUP_NAMES['directions']
    ng = _get_directions_geometry_nodegroup(ngn)

    # link modifier to object
    modifier = obj.modifiers.get(ngn) or obj.modifiers.new(name=ngn, type="NODES")
    if modifier is None: return False
    modifier.node_group = ng
    modifier.show_render = False
    modifier.show_viewport = True
    modifier.show_in_editmode = False
    return True

def remove_directions_geometry_nodegroup(obj):
    ngn = NODEGROUP_NAMES['directions']
    modifier = obj.modifiers.get(ngn)
    if modifier is not None:
        obj.modifiers.remove(modifier)
        #modifier.show_viewport = False

def is_directions_geometry_nodegroup_visible(obj):
    ngn = NODEGROUP_NAMES['directions']
    modifier = obj.modifiers.get(ngn)
    if modifier is None: return False
    return modifier.show_viewport
