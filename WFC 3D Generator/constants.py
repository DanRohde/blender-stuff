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
ANY_DIRECTIONS = { 'ANY_FACE' : (0,0,0), 'ANY_EDGE' : (0,0,0), 'ANY_CORNER' : (0,0,0), 'ANY' : (0,0,0),  }

DIRECTIONS = { **FACE_DIRECTIONS, **CORNER_DIRECTIONS, **EDGE_DIRECTIONS, **ANY_DIRECTIONS }

OPPOSITE_DIRECTIONS = { 'TOP':'BOTTOM', 'BOTTOM':'TOP', 'FRONT':'BACK', 'BACK':'FRONT', 'LEFT':'RIGHT', 'RIGHT':'LEFT', 
                       'CN_FBL':'CN_BTR', 'CN_BTR':'CN_FBL', 'CN_FBR':'CN_BTL', 'CN_BTL':'CN_FBR',
                       'CN_FTL':'CN_BBR', 'CN_BBR':'CN_FTL', 'CN_FTR':'CN_BBL', 'CN_BBL':'CN_FTR',
                       'EN_FL':'EN_BR', 'EN_BR':'EN_FL', 'EN_FR':'EN_BL', 'EN_BL':'EN_FR', 'EN_FT':'EN_BB','EN_BB':'EN_FT', 'EN_FB':'EN_BT','EN_BT':'EN_FB',
                       'EN_LT':'EN_RB', 'EN_RB':'EN_LT', 'EN_LB':'EN_RT', 'EN_RT':'EN_LB',
                       'ANY':'ANY', 'ANY_FACE':'ANY_FACE', 'ANY_EDGE':'ANY_EDGE', 'ANY_CORNER':'ANY_CORNER',
}
ROTATE_DIRECTIONS = {
    'X' :  { 'TOP' : 'BACK', 'BOTTOM' :'FRONT', 'FRONT' : 'TOP', 'BACK': 'BOTTOM', 'LEFT' : 'LEFT', 'RIGHT' : 'RIGHT',
              'CN_FBL' : 'CN_FTL', 'CN_BTR' : 'CN_BBR', 'CN_FBR' : 'CN_FTR', 'CN_BTL' : 'CN_BBL',
              'CN_FTL' : 'CN_BTL', 'CN_BBR' : 'CN_FBR', 'CN_FTR' : 'CN_BTR', 'CN_BBL' : 'CN_FBL',
              'EN_FL' : 'EN_LT', 'EN_BR' : 'EN_RB', 'EN_FR' : 'EN_RT', 'EN_BL' : 'EN_LB', 'EN_FT' : 'EN_BT','EN_BB':'EN_FB', 'EN_FB':'EN_FT','EN_BT':'EN_BB',
              'EN_LT' : 'EN_BL', 'EN_RB' : 'EN_FR', 'EN_LB' : 'EN_FL', 'EN_RT' : 'EN_BR', 'ANY' : 'ANY', 'ANY_FACE':'ANY_FACE', 'ANY_EDGE':'ANY_EDGE', 'ANY_CORNER':'ANY_CORNER',
    },
    'Y' :  { 'TOP' : 'LEFT', 'BOTTOM' : 'RIGHT', 'FRONT' : 'FRONT', 'BACK' : 'BACK', 'LEFT' : 'BOTTOM', 'RIGHT' : 'TOP',
              'CN_FBL' : 'CN_FBR', 'CN_BTR' : 'CN_BTL', 'CN_FBR' : 'CN_FTR', 'CN_BTL' : 'CN_BBL',
              'CN_FTL' : 'CN_FBL', 'CN_BBR' : 'CN_BTR', 'CN_FTR' : 'CN_FTL', 'CN_BBL' : 'CN_BBR',
              'EN_FL' : 'EN_FB', 'EN_BR' : 'EN_BT', 'EN_FR' : 'EN_FT', 'EN_BL' : 'EN_BB', 'EN_FT' : 'EN_FL','EN_BB':'EN_BR', 'EN_FB':'EN_FR','EN_BT':'EN_BL',
              'EN_LT' : 'EN_LB', 'EN_RB' : 'EN_RT', 'EN_LB' : 'EN_RB', 'EN_RT' : 'EN_LT', 'ANY' : 'ANY', 'ANY_FACE':'ANY_FACE', 'ANY_EDGE':'ANY_EDGE', 'ANY_CORNER':'ANY_CORNER',
    },
    'Z' : { 'TOP' : 'TOP', 'BOTTOM' : 'BOTTOM', 'FRONT' : 'LEFT', 'BACK' : 'RIGHT', 'LEFT' : 'BACK', 'RIGHT' : 'FRONT',
              'CN_FBL' : 'CN_BBL', 'CN_BTR' : 'CN_FTR', 'CN_FBR' : 'CN_FBL', 'CN_BTL' : 'CN_BTR',
              'CN_FTL' : 'CN_BTL', 'CN_BBR' : 'CN_FBR', 'CN_FTR' : 'CN_FTL', 'CN_BBL' : 'CN_BBR',
              'EN_FL' : 'EN_BL', 'EN_BR' : 'EN_FR', 'EN_FR' : 'EN_FL', 'EN_BL' : 'EN_BR', 'EN_FT' : 'EN_LT','EN_BB':'EN_RB', 'EN_FB':'EN_LB','EN_BT':'EN_RT',
              'EN_LT' : 'EN_BT', 'EN_RB' : 'EN_FB', 'EN_LB' : 'EN_BB', 'EN_RT' : 'EN_FT', 'ANY' : 'ANY', 'ANY_FACE':'ANY_FACE', 'ANY_EDGE':'ANY_EDGE', 'ANY_CORNER':'ANY_CORNER',
    },
}
ROTATE_DIMENSIONS = {
    'X' : { 0 : 0, 1 : 2, 2 : 1 },
    'Y' : { 0 : 2, 1 : 1, 2 : 0 },
    'Z' : { 0 : 1, 1 : 0, 2 : 2 },
}
PROP_DEFAULTS = {
    # neighbor constraints
    'left' : '', 'right' : '', 'top' : '', 'bottom' : '', 'front' : '', 'back' : '',
    'en_fl':'','en_fr':'','en_ft':'','en_fb':'','en_bl':'','en_br':'','en_bt':'','en_bb':'','en_lt':'','en_lb':'','en_rt':'','en_rb':'',
    'cn_fbl':'','cn_fbr':'','cn_ftl':'','cn_ftr':'','cn_bbl':'','cn_bbr':'','cn_btl':'','cn_btr':'',
    'any':'','any_face':'','any_edge':'','any_corner':'',
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
    'freq_grid' : -1, 'freq_grid_pct': -1, 'freq_neighbor' : -1, 'freq_axes' : (-1,-1,-1), 'freq_any_neighbor' : -1, 'freq_any_axes' : (-1,-1,-1),
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
    'region_level_ground': True, 'region_level_first': True, 'region_level_second': True, 'region_level_mid': True, 'region_level_penultimate': True, 'region_level_top': True,
    # connector constraints:
    'conn_left':'','conn_right':'','conn_top':'','conn_bottom':'','conn_back':'','conn_front':'',
    'conn_en_fl':'','conn_en_fr':'','conn_en_ft':'','conn_en_fb':'',
    'conn_en_bl':'','conn_en_br':'','conn_en_bt':'','conn_en_bb':'',
    'conn_en_lt':'','conn_en_lb':'','conn_en_rt':'','conn_en_rb':'',
    'conn_cn_fbl':'','conn_cn_fbr':'','conn_cn_ftl':'','conn_cn_ftr':'',
    'conn_cn_bbl':'','conn_cn_bbr':'','conn_cn_btl':'','conn_cn_btr':'',
    'conn_any':'','conn_any_face':'','conn_any_edge':'','conn_any_corner':'',
    # connector exclusion constraints:
    'conn_excl_name':'','conn_excl_direction': len(DIRECTIONS)-1,
    # multiple connector constraints:
    'mult_conn_name':'','mult_conn_direction': len(DIRECTIONS)-1,
    # dimensions constraints:
    'dim_xyz' : (1,1,1),
    # fixed position constraints:
    'fixed_position_xyz' : (0,0,0), 'fixed_position_pct' : (0,0,0), 'fixed_position_type' : 'absolute',
    # region frequency constraints:
    'regfreq_name' : '', 'regfreq_min' : (0,0,0), 'regfreq_max' : (0,0,0), 'regfreq_freq' : -1, 'regfreq_freq_pct' : -1,
    # noise constraints:
    'noise_prob_basis' : 0, 'noise_prob_threshold' : 1.0, 'noise_prob_scale' : 0.1,
    'noise_transf_function' : 1,
    'noise_transf_basis' : 0.0, 'noise_transf_scale' : 0.1, 'noise_randomize_position' : False,
    'noise_transf_h' : 1.0, 'noise_transf_octaves' : 0.0, 'noise_transf_lacunarity': 2.0,
    'noise_transf_offset' : 0.0, 'noise_transf_gain' : 1.0,
    # geo constraints:
    'geo_left': False, 'geo_right': False, 'geo_bottom': False, 'geo_top': False, 'geo_front': False, 'geo_back': False,
    'geo_match_edges': False, 'geo_match_faces': False,
    'geo_tolerance' : 0.001, 'geo_threshold' : 0.001,
    # region probability constraints:
    'regprob_name' : '', 'regprob_min' : (0,0,0), 'regprob_max' : (0,0,0), 'regprob_weight' : 1, 'regprob_probability' : 1,
    # distance constraints:
    'distance': (1,1,1), 'distance_from': 'object', 'distance_object': None, 'distance_position': (0,0,0), 'distance_position_type' : 'absolute', 'distance_position_pct' : (0,0,0),
    'distance_subcollection': None, 'distance_type' : 'minimum',
    # empty neighbor constraints:
    'empty_neighbor':   [], 'empty_any_neighbor': [],
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

FREQUENCY_CONSTRAINTS = [ 'freq_grid', 'freq_grid_pct', 'freq_neighbor', 'freq_neighbor_face', 'freq_neighbor_edge',
                          'freq_neighbor_corner', 'freq_axes', 'freq_any_neighbor',
                          'freq_any_neighbor_face', 'freq_any_neighbor_edge','freq_any_neighbor_corner', 'freq_any_axes',
]

PROBABILITY_CONSTRAINTS = [ 'probability', 'weight', 'auto_weight']

GRID_CONSTRAINTS = [ 'faces', 'corners', 'edges', 'inside']

REGION_CONSTRAINTS = [ 'region_min', 'region_max', 'region_quadrant', 'region_level_ground', 'region_level_first', 'region_level_second', 'region_level_mid', 'region_level_penultimate', 'region_level_top']

CONNECTOR_CONSTRAINTS = ['conn_left','conn_right','conn_front','conn_back','conn_top','conn_bottom',
                        'conn_en_fl','conn_en_fr','conn_en_ft','conn_en_fb',
                         'conn_en_bl','conn_en_br','conn_en_bt','conn_en_bb',
                         'conn_en_lt','conn_en_lb','conn_en_rt','conn_en_rb',
                         'conn_cn_fbl','conn_cn_fbr','conn_cn_ftl','conn_cn_ftr',
                         'conn_cn_bbl','conn_cn_bbr','conn_cn_btl','conn_cn_btr',
                         'conn_any','conn_any_face','conn_any_edge','conn_any_corner',
]
CONNECTOR_EXCLUSION_CONSTRAINTS = [ 'conn_excl_direction', 'conn_excl_name', ]

MULTIPLE_CONNECTOR_CONSTRAINTS = [ 'mult_conn_direction', 'mult_conn_name', ]

DIMENSIONS_CONSTRAINTS = [ 'dim_xyz' ]

FIXED_POSITION_CONSTRAINTS = [ 'fixed_position_xyz', 'fixed_position_pct', 'fixed_position_type' ]

REGFREQ_CONSTRAINTS = [ 'regfreq_name', 'regfreq_min', 'regfreq_max', 'regfreq_freq', 'regfreq_freq_pct',]

REGPROB_CONSTRAINTS = [ 'regprob_name', 'regprob_min', 'regprob_max', 'regprob_weight', 'regprob_probability',]

DISTANCE_CONSTRAINTS = [ 'distance', 'distance_from', 'distance_position', 'distance_position_type', 'distance_position_pct', 'distance_object', 'distance_subcollection', 'distance_type']

LIST_CONSTRAINTS = { 'regfreq_min' :'regfreq_input_list',
                     'regfreq_max' : 'regfreq_input_list',
                     'regfreq_freq' : 'regfreq_input_list',
                     'regfreq_freq_pct' : 'regfreq_input_list',
                     'regfreq_name' : 'regfreq_input_list',
                     'fixed_position_xyz' : 'fixed_position_input_list',
                     'fixed_position_pct' : 'fixed_position_input_list',
                     'fixed_position_type' : 'fixed_position_input_list',
                     'regprob_name' : 'regprob_input_list',
                     'regprob_min' : 'regprob_input_list',
                     'regprob_max' : 'regprob_input_list',
                     'regprob_weight' : 'regprob_input_list',
                     'regprob_probability' : 'regprob_input_list',
                     'distance' : 'distance_input_list',
                     'distance_from' : 'distance_input_list',
                     'distance_position' : 'distance_input_list',
                     'distance_position_pct' : 'distance_input_list',
                     'distance_position_type' : 'distance_input_list',
                     'distance_object' : 'distance_input_list',
                     'distance_subcollection' : 'distance_input_list',
                     'distance_type' : 'distance_input_list',
                     'conn_excl_name' : 'conn_excl_input_list',
                     'conn_excl_direction' : 'conn_excl_input_list',
                     'mult_conn_name' : 'mult_conn_input_list',
                     'mult_conn_direction' : 'mult_conn_input_list',
                   }
ENUM_CONSTRAINTS = { 'distance_from' : [ 'object', 'position', 'sub-collection'], 'distance_type' : [ 'minimum', 'maximum' ,'equal'],
                     'fixed_position_type' : [ 'absolute', 'pct'],
                     'distance_position_type' : [ 'absolute', 'pct'],
                     'conn_excl_direction' : list(DIRECTIONS.keys()),
                     'mult_conn_direction' : list(DIRECTIONS.keys()),
                     }

EMPTY_NEIGHBOR_CONSTRAINTS = [ 'empty_neighbor', 'empty_any_neighbor' ]
SELECTION_CONSTRAINTS = {
    'empty_neighbor' : 'empty_neighbor_list',
    'empty_any_neighbor' : 'empty_any_neighbor_list',
}

NOISE_CONSTRAINTS = [ 'noise_prob_basis' , 'noise_prob_threshold', 'noise_prob_scale',
                      'noise_transf_basis', 'noise_transf_scale', 'noise_randomize_position',
                      'noise_transf_function',
                      'noise_transf_h', 'noise_transf_octaves', 'noise_transf_lacunarity',
                      'noise_transf_offset', 'noise_transf_gain',
                    ]

GEOMETRY_CONSTRAINTS = [ 'geo_top', 'geo_bottom', 'geo_left', 'geo_right', 'geo_front', 'geo_back', 'geo_match_edges', 'geo_match_faces', 'geo_tolerance', 'geo_threshold']

GEN_CONSTRAINTS = (SYMMETRY_CONSTRAINTS + TRANSFORMATION_CONSTRAINTS + FREQUENCY_CONSTRAINTS + PROBABILITY_CONSTRAINTS
                   + REGION_CONSTRAINTS + FIXED_POSITION_CONSTRAINTS + DIMENSIONS_CONSTRAINTS + REGFREQ_CONSTRAINTS
                   + CONNECTOR_EXCLUSION_CONSTRAINTS + MULTIPLE_CONNECTOR_CONSTRAINTS
                   + NOISE_CONSTRAINTS + GEOMETRY_CONSTRAINTS + REGPROB_CONSTRAINTS + DISTANCE_CONSTRAINTS + EMPTY_NEIGHBOR_CONSTRAINTS)

DEFAULT_EMPTY_NAME = '_WFC3D_DEFAULTS_'

DIR_TRANSLATION = { 'TOP': 'top face', 'BOTTOM' : 'bottom face', 'LEFT' : 'left face', 'RIGHT': 'right face', 'FRONT' : 'front face', 'BACK' : 'back face',
                 'FBL':'front bottom left corner', 'FBR' : 'front bottom right corner', 'FTL' : 'front top left corner', 'FTR' : 'front top right corner',
                 'BBL':'back bottom left corner', 'BBR' : 'back bottom right corner', 'BTL' : 'back top left corner', 'BTR' : 'back top right corner',
                 'CN_FBL':'front bottom left corner', 'CN_FBR' : 'front bottom right corner', 'CN_FTL' : 'front top left corner', 'CN_FTR' : 'front top right corner',
                 'CN_BBL':'back bottom left corner', 'CN_BBR' : 'back bottom right corner', 'CN_BTL' : 'back top left corner', 'CN_BTR' : 'back top right corner',
                 'FL':'front left edge', 'FR': 'front right edge', 'FB' : 'front bottom edge', 'FT' : 'front top edge',
                 'BL':'back left edge', 'BR': 'back right edge', 'BB' : 'back bottom edge', 'BT' : 'back top edge',
                 'LT':'left top edge', 'LB' : 'left bottom edge', 'RT' : 'right top edge', 'RB' : 'right bottom edge',
                 'EN_FL':'front left edge', 'EN_FR': 'front right edge', 'EN_FB' : 'front bottom edge', 'EN_FT' : 'front top edge',
                 'EN_BL':'back left edge', 'EN_BR': 'back right edge', 'EN_BB' : 'back bottom edge', 'EN_BT' : 'back top edge',
                 'EN_LT':'left top edge', 'EN_LB' : 'left bottom edge', 'EN_RT' : 'right top edge', 'EN_RB' : 'right bottom edge',
                 'ANY': 'any direction', 'ANY_FACE' : 'any face direction', 'ANY_EDGE' : 'any edge direction', 'ANY_CORNER' : 'any corner direction',
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

HELP = {
    'constraints' : {
        'url' : 'https://github.com/DanRohde/blender-stuff/blob/main/WFC%203D%20Generator/constraints.md',
        'anchormap' : { '_none_': 'constraints', 'transformations' : 'transformations', 'neighbor' : 'neighbor-constraints', 'connector' : 'connector-constraints', 'geometry': 'geometry-constraints',
                      'regfreq' : 'region-frequency-constraints', 'noise' : 'noise-constraints', 'regprob' : 'region-probability-constraints', 'grid': 'grid-constraints',
                      'dimensions' : 'dimensions-constraints', 'fixed_position' : 'fixed-position-constraints', 'region' : 'region-constraints', 'distance' : 'distance-constraints',
                      'frequency' : 'frequency-constraints', 'symmetry' : 'symmetry-constraints', 'probability' : 'probability-constraints', 'empty':'empty-neighbor-constraints',
                        'connector_exclusion' : 'connector-exclusion-constraints', 'multiple_connector' : 'multiple-connector-constraints',
                      }
    }
}

CONSTRAINTS_MENU = [("_none_","Select a Constraint Type","Select a constraint type"),
               None,
               ("neighbor","Neighbor Constraints","Neighbor constraints"),
               ('connector', 'Connector Constraints', 'Connector constraints'),
               ('connector_exclusion', 'Connector Exclusion Constraints', 'Connector exclusion constraints'),
               ('multiple_connector', 'Multiple Connector Constraints', 'Multiple Connector constraints'),
               ('geometry', 'Geometry Constraints', 'Geometry constraints'),
               ('empty', 'Empty Neighbor Constraints', 'Empty Neighbor constraints'),
               None,
               ('dimensions', 'Dimensions Constraints', 'Dimensions constraints'),
               ('fixed_position', 'Fixed Position Constraints', 'Fixed position constraints'),
               ("grid","Grid Constraints","Grid constraints"),("region","Region Constraints","Region constraints"),
               ('distance','Distance Constraints','Distance constraints'),
               ('frequency',"Frequency Constraints","Frequency constraints"), ('regfreq','Region Frequency Constraints','Region Frequency constraints'),
               ("symmetry","Symmetry Constraints","Symmetry constraints"),
               None,
               ("probability", "Probability Constraints", "Probability constraints"),
               ("regprob", "Region Probability Constraints", "Region Probability constraints"),
               None,
               ("transformations", "Transformations", "Transformations"),
               ("noise","Noise Constraints","Noise constraints"),
               ]
NOISE_FUNCTIONS = [
    ('_NONE_', 'Please select a noise function', 'Please select a noise function'),
    ('N', 'Noise', 'Noise'),
    ('MF', 'Multifractal', 'Multifractal'),
    ('RMF', 'Ridged Multifractal', 'Ridged Multifractal'),
    ('HMF', 'Hybrid Multifractal', 'Hybrid Multifractal'),
    ('jBM', 'jBM', 'jBM' ),
    ('HT',  'Hetero Terrain', 'Hetero Terrain'),
]
NOISE_BASIS = {
    'BLENDER' : 'Blender', 'PERLIN_ORIGINAL' : 'Perlin (original)', 'PERLIN_NEW' : 'Perlin new',
    'VORONOI_F1' : 'Voronoi F1', 'VORONOI_F2' : 'Voronoi F2', 'VORONOI_F3' : 'Voronoi F3', 'VORONOI_F4' : 'Voronoi F4',
    'VORONOI_F2F1' : 'Voronoi F2F1', 'VORONOI_CRACKLE' : 'Voronoi crackle', 'CELLNOISE' : 'Cell noise'
}