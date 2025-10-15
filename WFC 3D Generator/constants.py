DIRECTIONS = {
    'TOP': (0, 0, 1), 'BOTTOM': (0, 0, -1), 'FRONT': (0, -1, 0), 'BACK': (0, 1, 0), 'LEFT': (-1, 0, 0), 'RIGHT': (1, 0, 0),
    'CN_FBL' : (-1,-1,-1), 'CN_FBR' : (1,-1,-1), 'CN_FTL' : (-1,-1,1), 'CN_FTR' : (1,-1,1),
    'CN_BBL' : (-1,1,-1), 'CN_BBR' : (1,1,-1), 'CN_BTL' : (-1,1,1), 'CN_BTR' : (1,1,1),
    'EN_FL' : (-1,-1,0), 'EN_FR' : (1,-1,0), 'EN_FB' : (0,-1,-1), 'EN_FT' : (0,-1,1),
    'EN_BL' : (-1,1,0), 'EN_BR' : (1,1,0), 'EN_BB' : (0,1,-1), 'EN_BT' : (0,1,1),
    'EN_LB' : (-1,0,-1), 'EN_LT' : (-1,0,1), 'EN_RB' : (1,0,-1), 'EN_RT' : (1,0,1),
}
PROP_DEFAULTS = {
    # neighbor constraints
    'left' : '', 'right' : '', 'top' : '', 'bottom' : '', 'front' : '', 'back' : '', 
    'en_fl':'','en_fr':'','en_ft':'','en_fb':'','en_bl':'','en_br':'','en_bt':'','en_bb':'','en_lt':'','en_lb':'','en_rt':'','en_rb':'',
    'cn_fbl':'','cn_fbr':'','cn_ftl':'','cn_ftr':'','cn_bbl':'','cn_bbr':'','cn_btl':'','cn_btr':'',
    # weight constraints:
    'weight' : 1, 
    # grid constraints:
    'corners' : '', 'edges' : '', 'faces' : '','inside' : '',
    #transformation constraints:
    'translation_min' : (0,0,0), 'translation_max' : (0,0,0), 'translation_steps' : (0,0,0),
    'rotation_min' : (0,0,0), 'rotation_max': (0,0,0), 'rotation_steps' : (0,0,0),
    'rotation_grid' : (False,False,False), 'rotation_neighbor' : (False,False, False),
    'scale_min' : (1,1,1), 'scale_max' : (1,1,1), 'scale_steps' : (0,0,0), 
    'scale_type' : 0, 'scale_uni': (0,0,0),
}

TRANSFORMATION_CONSTRAINTS = ('scale_min','scale_max','scale_steps','scale_type', 'scale_uni',
                                  'rotation_min','rotation_max','rotation_steps',
                                  #'rotation_neighbor','rotation_grid',
                                  'translation_min','translation_max','translation_steps')