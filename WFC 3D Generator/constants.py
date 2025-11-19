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
ANY_DIRECTION = { 'ANY' : (0,0,0) }

DIRECTIONS = { **FACE_DIRECTIONS, **CORNER_DIRECTIONS, **EDGE_DIRECTIONS, **ANY_DIRECTION }

OPPOSITE_DIRECTIONS = { 'TOP':'BOTTOM', 'BOTTOM':'TOP', 'FRONT':'BACK', 'BACK':'FRONT', 'LEFT':'RIGHT', 'RIGHT':'LEFT', 
                       'CN_FBL':'CN_BTR', 'CN_BTR':'CN_FBL', 'CN_FBR':'CN_BTL', 'CN_BTL':'CN_FBR',
                       'CN_FTL':'CN_BBR', 'CN_BBR':'CN_FTL', 'CN_FTR':'CN_BBL', 'CN_BBL':'CN_FTR',
                       'EN_FL':'EN_BR', 'EN_BR':'EN_FL', 'EN_FR':'EN_BL', 'EN_BL':'EN_FR', 'EN_FT':'EN_BB','EN_BB':'EN_FT', 'EN_FB':'EN_BT','EN_BT':'EN_FB',
                       'EN_LT':'EN_RB', 'EN_RB':'EN_LT', 'EN_LB':'EN_RT', 'EN_RT':'EN_LB',
                       'ANY':'ANY',
}
ROTATE_DIRECTIONS = {
    'X' : {
        1 : { 'TOP' : 'BACK', 'BOTTOM' :'FRONT', 'FRONT' : 'TOP', 'BACK': 'BOTTOM', 'LEFT' : 'LEFT', 'RIGHT' : 'RIGHT',
              'CN_FBL' : 'CN_FTL', 'CN_BTR' : 'CN_BBR', 'CN_FBR' : 'CN_FTR', 'CN_BTL' : 'CN_BBL',
              'CN_FTL' : 'CN_BTL', 'CN_BBR' : 'CN_FBR', 'CN_FTR' : 'CN_BTR', 'CN_BBL' : 'CN_FBL',
              'EN_FL' : 'EN_LT', 'EN_BR' : 'EN_RB', 'EN_FR' : 'EN_RT', 'EN_BL' : 'EN_LB', 'EN_FT' : 'EN_BT','EN_BB':'EN_FB', 'EN_FB':'EN_FT','EN_BT':'EN_BB',
              'EN_LT' : 'EN_BL', 'EN_RB' : 'EN_FR', 'EN_LB' : 'EN_FL', 'EN_RT' : 'EN_BR', 'ANY' : 'ANY',
        },
    },
    'Y' : {
        1 : { 'TOP' : 'LEFT', 'BOTTOM' : 'RIGHT', 'FRONT' : 'FRONT', 'BACK' : 'BACK', 'LEFT' : 'BOTTOM', 'RIGHT' : 'TOP',
              'CN_FBL' : 'CN_FBR', 'CN_BTR' : 'CN_BTL', 'CN_FBR' : 'CN_FTR', 'CN_BTL' : 'CN_BBL',
              'CN_FTL' : 'CN_FBL', 'CN_BBR' : 'CN_BTR', 'CN_FTR' : 'CN_FTL', 'CN_BBL' : 'CN_BBR',
              'EN_FL' : 'EN_FB', 'EN_BR' : 'EN_BT', 'EN_FR' : 'EN_FT', 'EN_BL' : 'EN_BB', 'EN_FT' : 'EN_FL','EN_BB':'EN_BR', 'EN_FB':'EN_FR','EN_BT':'EN_BL',
              'EN_LT' : 'EN_LB', 'EN_RB' : 'EN_RT', 'EN_LB' : 'EN_RB', 'EN_RT' : 'EN_LT', 'ANY' : 'ANY',
        }
    },
    'Z' : {
        1 : { 'TOP' : 'TOP', 'BOTTOM' : 'BOTTOM', 'FRONT' : 'LEFT', 'BACK' : 'RIGHT', 'LEFT' : 'BACK', 'RIGHT' : 'FRONT',
              'CN_FBL' : 'CN_BBL', 'CN_BTR' : 'CN_FTR', 'CN_FBR' : 'CN_FBL', 'CN_BTL' : 'CN_BTR',
              'CN_FTL' : 'CN_BTL', 'CN_BBR' : 'CN_FBR', 'CN_FTR' : 'CN_FTL', 'CN_BBL' : 'CN_BBR',
              'EN_FL' : 'EN_BL', 'EN_BR' : 'EN_FR', 'EN_FR' : 'EN_FL', 'EN_BL' : 'EN_BR', 'EN_FT' : 'EN_LT','EN_BB':'EN_RB', 'EN_FB':'EN_LB','EN_BT':'EN_RT',
              'EN_LT' : 'EN_BT', 'EN_RB' : 'EN_FB', 'EN_LB' : 'EN_BB', 'EN_RT' : 'EN_FT', 'ANY' : 'ANY',
        }
    }
}

PROP_DEFAULTS = {
    # neighbor constraints
    'left' : '', 'right' : '', 'top' : '', 'bottom' : '', 'front' : '', 'back' : '',
    'en_fl':'','en_fr':'','en_ft':'','en_fb':'','en_bl':'','en_br':'','en_bt':'','en_bb':'','en_lt':'','en_lb':'','en_rt':'','en_rb':'',
    'cn_fbl':'','cn_fbr':'','cn_ftl':'','cn_ftr':'','cn_bbl':'','cn_bbr':'','cn_btl':'','cn_btr':'',
    'any':'',
    'allow_neighbor_constraint_violations':False,
    # probability constraints:
    'weight' : 1, 'probability' : 1, 'auto_weight' : False,
    # grid constraints:
    'corners' : '', 'edges' : '', 'faces' : '','inside' : '',
    #transformation constraints:
    'translation_min' : (0,0,0), 'translation_max' : (0,0,0), 'translation_steps' : (0,0,0),
    'rotation_min' : (0,0,0), 'rotation_max': (0,0,0), 'rotation_steps' : (0,0,0),
    'scale_min' : (1,1,1), 'scale_max' : (1,1,1), 'scale_steps' : (0,0,0), 
    'scale_type' : 0, 'scale_uni': (1,1,0), 'flipping' : (0, 0, 0),
    # frequency constraints:
    'freq_grid' : -1, 'freq_neighbor' : -1, 'freq_axes' : (-1,-1,-1), 'freq_any_neighbor' : -1, 'freq_any_axes' : (-1,-1,-1),
    'freq_neighbor_face': -1, 'freq_neighbor_edge' : -1, 'freq_neighbor_corner' : -1,
    'freq_any_neighbor_face': -1, 'freq_any_neighbor_edge' : -1, 'freq_any_neighbor_corner' : -1,
    # symmetry constraints:
    'sym_mirror_axes': (False, False, False), 'sym_rotate_axis' : (-1,-1,-1), 'sym_rotate_n': -1, 'sym_mirror_axes_rotate' : False,
    'sym_mirror_axes_x':None, 'sym_mirror_axes_y':None, 'sym_mirror_axes_z':None, 'sym_mirror_axes_xy':None,
    'sym_mirror_axes_xz':None, 'sym_mirror_axes_yz':None, 'sym_mirror_axes_xyz':None,
    'sym_mirror_flip_x':False, 'sym_mirror_flip_y':False, 'sym_mirror_flip_z':False, 'sym_mirror_flip_xy':False,
    'sym_mirror_flip_xz':False, 'sym_mirror_flip_yz':False, 'sym_mirror_flip_xyz':False,
    'sym_mirror_trans': False, 'sym_mirror_flip_transl':False,
    # region constraints:
    'region_min':(-1,-1,-1), 'region_max':(-1,-1,-1), 'region_quadrant': (True,)*8,
    # connector constraints:
    'conn_left':'','conn_right':'','conn_top':'','conn_bottom':'','conn_back':'','conn_front':'',
    'conn_en_fl':'','conn_en_fr':'','conn_en_ft':'','conn_en_fb':'',
    'conn_en_bl':'','conn_en_br':'','conn_en_bt':'','conn_en_bb':'',
    'conn_en_lt':'','conn_en_lb':'','conn_en_rt':'','conn_en_rb':'',
    'conn_cn_fbl':'','conn_cn_fbr':'','conn_cn_ftl':'','conn_cn_ftr':'',
    'conn_cn_bbl':'','conn_cn_bbr':'','conn_cn_btl':'','conn_cn_btr':'',
    'conn_any':'',
    # dimensions constraints:
    'dim_xyz' : (1,1,1),
    # fixed position constraints:
    'fixed_position_xyz' : (-1,-1,-1),
    # region frequency constraints:
    'regfreq_name' : '', 'regfreq_min' : (-1,-1,-1), 'regfreq_max' : (-1,-1,-1), 'regfreq_freq' : -1,
    # noise constraints:
    'noise_prob_basis' : 0, 'noise_prob_threshold' : 1.0, 'noise_prob_scale' : .1,
    'noise_transf_basis' : 0, 'noise_transf_scale' : .1,
    # geo constraints:
    'geo_faces' : (False, False, False, False, False, False), 'geo_match_edges': False, 'geo_match_faces': False,
    'geo_tolerance' : 0,
    # region probability constraints:
    'regprob_name' : '', 'regprob_min' : (-1,-1,-1), 'regprob_max' : (-1,-1,-1), 'regprob_weight' : 1, 'regprob_probability' : 1,
}

ADD_NEIGHBOR_CONSTRAINTS = ['allow_neighbor_constraint_violations' ]

SYMMETRY_CONSTRAINTS = [ 'sym_mirror_axes','sym_rotate_axis', 'sym_rotate_n', 'sym_mirror_axes_rotate',
                         'sym_mirror_axes_x', 'sym_mirror_axes_y', 'sym_mirror_axes_z', 'sym_mirror_axes_xy',
                         'sym_mirror_axes_xz' , 'sym_mirror_axes_yz', 'sym_mirror_axes_xyz',
                         'sym_mirror_flip_x', 'sym_mirror_flip_y', 'sym_mirror_flip_z', 'sym_mirror_flip_xy',
                         'sym_mirror_flip_xz', 'sym_mirror_flip_yz', 'sym_mirror_flip_xyz', 'sym_mirror_flip_transl',
                         'sym_mirror_trans',
                         ]
TRANSFORMATION_CONSTRAINTS = [ 'translation_min', 'translation_max', 'translation_steps',
                               'rotation_min', 'rotation_max', 'rotation_steps',
                               'scale_type', 'scale_min', 'scale_max', 'scale_steps', 'scale_uni',
                               'flipping']

FREQUENCY_CONSTRAINTS = [ 'freq_grid', 'freq_neighbor', 'freq_neighbor_face', 'freq_neighbor_edge',
                          'freq_neighbor_corner', 'freq_axes', 'freq_any_neighbor',
                          'freq_any_neighbor_face', 'freq_any_neighbor_edge','freq_any_neighbor_corner', 'freq_any_axes',
]

PROBABILITY_CONSTRAINTS = [ 'probability', 'weight', 'auto_weight']

GRID_CONSTRAINTS = [ 'faces', 'corners', 'edges', 'inside']

REGION_CONSTRAINTS = [ 'region_min', 'region_max', 'region_quadrant']

CONNECTOR_CONSTRAINTS = ['conn_left','conn_right','conn_front','conn_back','conn_top','conn_bottom',
                        'conn_en_fl','conn_en_fr','conn_en_ft','conn_en_fb',
                         'conn_en_bl','conn_en_br','conn_en_bt','conn_en_bb',
                         'conn_en_lt','conn_en_lb','conn_en_rt','conn_en_rb',
                         'conn_cn_fbl','conn_cn_fbr','conn_cn_ftl','conn_cn_ftr',
                         'conn_cn_bbl','conn_cn_bbr','conn_cn_btl','conn_cn_btr',
                         'conn_any',
]

DIMENSIONS_CONSTRAINTS = [ 'dim_xyz' ]

FIXED_POSITION_CONSTRAINTS = [ 'fixed_position_xyz' ]

REGFREQ_CONSTRAINTS = [ 'regfreq_name', 'regfreq_min', 'regfreq_max', 'regfreq_freq',]

REGPROB_CONSTRAINTS = [ 'regprob_name', 'regprob_min', 'regprob_max', 'regprob_weight', 'regprob_probability']

LIST_CONSTRAINTS = { 'regfreq_min' :'regfreq_input_list',
                     'regfreq_max' : 'regfreq_input_list',
                     'regfreq_freq' : 'regfreq_input_list',
                     'regfreq_name' : 'regfreq_input_list',
                     'fixed_position_xyz' : 'fixed_position_input_list',
                     'regprob_name' : 'regprob_input_list',
                     'regprob_min' : 'regprob_input_list',
                     'regprob_max' : 'regprob_input_list',
                     'regprob_weight' : 'regprob_input_list',
                     'regprob_probability' : 'regprob_input_list',
                   }

NOISE_CONSTRAINTS = [ 'noise_prob_basis' , 'noise_prob_threshold', 'noise_prob_scale',
                      'noise_transf_basis', 'noise_transf_scale',
                    ]

GEOMETRY_CONSTRAINTS = [ 'geo_faces', 'geo_match_edges', 'geo_match_faces', 'geo_tolerance',]

GEN_CONSTRAINTS = (SYMMETRY_CONSTRAINTS + TRANSFORMATION_CONSTRAINTS + FREQUENCY_CONSTRAINTS + PROBABILITY_CONSTRAINTS
                   + REGION_CONSTRAINTS + FIXED_POSITION_CONSTRAINTS + DIMENSIONS_CONSTRAINTS + REGFREQ_CONSTRAINTS
                   + NOISE_CONSTRAINTS + GEOMETRY_CONSTRAINTS + REGPROB_CONSTRAINTS )

DEFAULT_EMPTY_NAME = '_WFC3D_DEFAULTS_'

DIR_TRANSLATION = { 'TOP': 'top face', 'BOTTOM' : 'bottom face', 'LEFT' : 'left face', 'RIGHT': 'right face', 'FRONT' : 'front face', 'BACK' : 'back face',
                 'FBL':'front bottom left corner', 'FBR' : 'front bottom right corner', 'FTL' : 'front top left corner', 'FTR' : 'front top right corner',
                 'BBL':'back bottom left corner', 'BBR' : 'back bottom right corner', 'BTL' : 'back top left corner', 'BTR' : 'back top right corner',
                 'FL':'front left edge', 'FR': 'front right edge', 'FB' : 'front bottom edge', 'FT' : 'front top edge',
                 'BL':'back left edge', 'BR': 'back right edge', 'BB' : 'back bottom edge', 'BT' : 'back top edge',
                 'LT':'left top edge', 'LB' : 'left bottom edge', 'RT' : 'right top edge', 'RB' : 'right bottom edge',
                 'ANY': 'any direction',
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
        'GREASEPENCIL': 'OUTLINER_OB_GREASEPENCIL',
        'CAMERA': 'OUTLINER_OB_CAMERA',
        'LIGHT': 'OUTLINER_OB_LIGHT',
        'SPEAKER': 'OUTLINER_OB_SPEAKER',
        'LIGHT_PROBE': 'OUTLINER_OB_LIGHTPROBE',
        'VOLUME': 'OUTLINER_OB_VOLUME',
        'POINTCLOUD': 'OUTLINER_OB_POINTCLOUD',
        'CURVES': 'OUTLINER_OB_CURVES',
        'COLLECTION' : 'GROUP',
        'OBJECT' : 'OUTLINER_OB_MESH',
}

NODEGROUP_NAMES = {
    'directions' : 'WFC 3D Directions',
}
CHERRY_PICKING_DELAY = 3