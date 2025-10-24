FACE_DIRECTIONS = {
    'TOP': (0, 0, 1), 'BOTTOM': (0, 0, -1), 'FRONT': (0, -1, 0), 'BACK': (0, 1, 0), 'LEFT': (-1, 0, 0), 'RIGHT': (1, 0, 0),
} 
CORNER_DIRECTIONS = {
    'CN_FBL' : (-1,-1,-1), 'CN_FBR' : (1,-1,-1), 'CN_FTL' : (-1,-1,1), 'CN_FTR' : (1,-1,1),
    'CN_BBL' : (-1,1,-1), 'CN_BBR' : (1,1,-1), 'CN_BTL' : (-1,1,1), 'CN_BTR' : (1,1,1),    
}
EDGE_DIRECTIONS = {
    'EN_FL' : (-1,-1,0), 'EN_FR' : (1,-1,0), 'EN_FB' : (0,-1,-1), 'EN_FT' : (0,-1,1),
    'EN_BL' : (-1,1,0), 'EN_BR' : (1,1,0), 'EN_BB' : (0,1,-1), 'EN_BT' : (0,1,1),
    'EN_LB' : (-1,0,-1), 'EN_LT' : (-1,0,1), 'EN_RB' : (1,0,-1), 'EN_RT' : (1,0,1),
}
DIRECTIONS = { **FACE_DIRECTIONS, **CORNER_DIRECTIONS, **EDGE_DIRECTIONS }

OPPOSITE_DIRECTIONS = { 'TOP':'BOTTOM', 'BOTTOM':'TOP', 'FRONT':'BACK', 'BACK':'FRONT', 'LEFT':'RIGHT', 'RIGHT':'LEFT', 
                       'CN_FBL':'CN_BTR', 'CN_BTR':'CN_FBL', 'CN_FBR':'CN_BTL', 'CN_BTL':'CN_FBR',
                       'CN_FTL':'CN_BBR', 'CN_BBR':'CN_FTL', 'CN_FTR':'CN_BBL', 'CN_BBL':'CN_FTR',
                       'EN_FL':'EN_BR', 'EN_BR':'EN_FL', 'EN_FR':'EN_BL', 'EN_BL':'EN_FR', 'EN_FT':'EN_BB','EN_BB':'EN_FT', 'EN_FB':'EN_BT','EN_BT':'EN_FB',
                       'EN_LT':'EN_RB', 'EN_RB':'EN_LT', 'EN_LB':'EN_RT', 'EN_RT':'EN_LB',     
}

PROP_DEFAULTS = {
    # neighbor constraints
    'left' : '', 'right' : '', 'top' : '', 'bottom' : '', 'front' : '', 'back' : '', 
    'en_fl':'','en_fr':'','en_ft':'','en_fb':'','en_bl':'','en_br':'','en_bt':'','en_bb':'','en_lt':'','en_lb':'','en_rt':'','en_rb':'',
    'cn_fbl':'','cn_fbr':'','cn_ftl':'','cn_ftr':'','cn_bbl':'','cn_bbr':'','cn_btl':'','cn_btr':'',
    'allow_neighbor_constraint_violations':False,
    # probability constraints:
    'weight' : 1, 'probability' : 1,
    # grid constraints:
    'corners' : '', 'edges' : '', 'faces' : '','inside' : '',
    #transformation constraints:
    'translation_min' : (0,0,0), 'translation_max' : (0,0,0), 'translation_steps' : (0,0,0),
    'rotation_min' : (0,0,0), 'rotation_max': (0,0,0), 'rotation_steps' : (0,0,0),
    'rotation_grid' : (False,False,False), 'rotation_neighbor' : (False,False, False),
    'scale_min' : (1,1,1), 'scale_max' : (1,1,1), 'scale_steps' : (0,0,0), 
    'scale_type' : 0, 'scale_uni': (1,1,0),
    # frequency constraints:
    'freq_grid' : -1, 'freq_neighbor' : -1, 'freq_axes' : (-1,-1,-1), 'freq_any_neighbor' : -1, 'freq_any_axes' : (-1,-1,-1),
    'freq_neighbor_face': -1, 'freq_neighbor_edge' : -1, 'freq_neighbor_corner' : -1,
    'freq_any_neighbor_face': -1, 'freq_any_neighbor_edge' : -1, 'freq_any_neighbor_corner' : -1,
    # symmetry constraints:
    'sym_mirror_axes': (False, False, False), 'sym_rotate_axis' : (-1,-1,-1), 'sym_rotate_n': -1, 'sym_mirror_axes_rotate' : False,
    # region constraints:
    'region_min':(-1,-1,-1), 'region_max':(-1,-1,-1), 'region_quadrant': (True,)*8,
    # connector constraints:
    'conn_left':'','conn_right':'','conn_top':'','conn_bottom':'','conn_back':'','conn_front':'',
    'conn_en_fl':'','conn_en_fr':'','conn_en_ft':'','conn_en_fb':'',
    'conn_en_bl':'','conn_en_br':'','conn_en_bt':'','conn_en_bb':'',
    'conn_en_lt':'','conn_en_lb':'','conn_en_rt':'','conn_en_rb':'',
    'conn_cn_fbl':'','conn_cn_fbr':'','conn_cn_ftl':'','conn_cn_ftr':'',
    'conn_cn_bbl':'','conn_cn_bbr':'','conn_cn_btl':'','conn_cn_btr':'',
}

ADD_NEIGHBOR_CONSTRAINTS = ['allow_neighbor_constraint_violations' ]

SYMMETRY_CONSTRAINTS = [ 'sym_mirror_axes','sym_rotate_axis', 'sym_rotate_n', 'sym_mirror_axes_rotate' ]
TRANSFORMATION_CONSTRAINTS = ['scale_min','scale_max','scale_steps','scale_type', 'scale_uni',
                                  'rotation_min','rotation_max','rotation_steps',
                                  #'rotation_neighbor','rotation_grid',
                                  'translation_min','translation_max','translation_steps']

FREQUENCY_CONSTRAINTS = [ 'freq_grid', 'freq_neighbor', 'freq_axes', 'freq_any_neighbor', 'freq_any_axes', 
                         'freq_neighbor_face', 'freq_neighbor_edge','freq_neighbor_corner',
                         'freq_any_neighbor_face', 'freq_any_neighbor_edge','freq_any_neighbor_corner',
]

PROBABILITY_CONSTRAINTS = [ 'weight', 'probability']

GRID_CONSTRAINTS = [ 'faces', 'corners', 'edges', 'inside']

REGION_CONSTRAINTS = [ 'region_min', 'region_max','region_quadrant']

CONNECTOR_CONSTRAINTS = ['conn_left','conn_right','conn_front','conn_back','conn_top','conn_bottom',
                        'conn_en_fl','conn_en_fr','conn_en_ft','conn_en_fb',
                         'conn_en_bl','conn_en_br','conn_en_bt','conn_en_bb',
                         'conn_en_lt','conn_en_lb','conn_en_rt','conn_en_rb',
                         'conn_cn_fbl','conn_cn_fbr','conn_cn_ftl','conn_cn_ftr',
                         'conn_cn_bbl','conn_cn_bbr','conn_cn_btl','conn_cn_btr',
]

DEFAULT_EMPTY_NAME = '_WFC3D_DEFAULTS_'

DIR_TRANSLATION = { 'TOP': 'top face', 'BOTTOM' : 'bottom face', 'LEFT' : 'left face', 'RIGHT': 'right face', 'FRONT' : 'front face', 'BACK' : 'back face',
                 'FBL':'front bottom left corner', 'FBR' : 'front bottom right corner', 'FTL' : 'front top left corner', 'FTR' : 'front top right corner',
                 'BBL':'back bottom left corner', 'BBR' : 'back bottom right corner', 'BTL' : 'back top left corner', 'BTR' : 'back top right corner',
                 'FL':'front left edge', 'FR': 'front right edge', 'FB' : 'front bottom edge', 'FT' : 'front top edge',
                 'BL':'back left edge', 'BR': 'back right edge', 'BB' : 'back bottom edge', 'BT' : 'back top edge',
                 'LT':'left top edge', 'LB' : 'left bottom edge', 'RT' : 'right top edge', 'RB' : 'right bottom edge',
}

ICON_MAP = {
        'MESH': 'OUTLINER_OB_MESH',
        'CURVE': 'OUTLINER_OB_CURVE',
        'SURFACE': 'OUTLINER_OB_SURFACE',
        'META': 'OUTLINER_OB_META',
        'FONT': 'OUTLINER_OB_FONT',
        'ARMATURE': 'OUTLINER_OB_ARMATURE',
        'LATTICE': 'OUTLINER_OB_LATTICE',
        'EMPTY': 'OUTLINER_OB_EMPTY',
        'GPENCIL': 'OUTLINER_OB_GREASEPENCIL',
        'CAMERA': 'OUTLINER_OB_CAMERA',
        'LIGHT': 'OUTLINER_OB_LIGHT',
        'SPEAKER': 'OUTLINER_OB_SPEAKER',
        'LIGHT_PROBE': 'OUTLINER_OB_LIGHTPROBE',
        'VOLUME': 'OUTLINER_OB_VOLUME',
        'POINTCLOUD': 'OUTLINER_OB_POINTCLOUD',
        'CURVES': 'OUTLINER_OB_CURVES'
}