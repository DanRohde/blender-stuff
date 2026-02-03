COLORS = [
    (0, 0, 1, 1), # BLUE
    (1, 0, 0, 1), # RED
    (1, 1, 0, 1), # YELLOW
    (0, 1, 0, 1), # GREEN
    (.49, 0, .13, 1), # DARK RED
    (.51, .79, 1, 1), # LIGHT BLUE
    (.19, .25, .02, 1), # DARK GREEN
    (1, 0, 1, 1), # PINK
    (1, 1, 1, 1), # WHITE
    (0, 1, 1, 1), # CYAN
    (0, 0, 0, 1)  # BLACK
]


ICONS = {
    "quickcharts" : "quickcharts.png",
    "header_label" : "labels_header.png",
    "header-left_label" : "labels_header_left.png",
    "left_label" :  "labels_left.png",
    "columns_series" : "columns_series.png",
    "rows_series" : "rows_series.png",
    "column_chart" : "column_chart.png",
    "bar_chart" : "bar_chart.png",
    "donut_chart" : "donut_chart.png",
    #"bc_subtype_deep" : "bc_subtype_deep.png",
    #"bc_subtype_stacked" : "bc_subtype_stacked.png",
    #"bc_subtype_percstacked" : "bc_subtype_percstacked.png",
    #"bc_subtype_normal" : "bc_subtype_normal.png",
    #"bar_shape" : "bar_shape.png",
    #"cylinder_shape" : "cylinder_shape.png",
    #"cone_shape" : "cone_shape.png",
    #"pyramid_shape" : "pyramid_shape.png",
}

CHART_TYPES = [
            ("column","Column Chart","Column chart"),
            ("bar","Bar Chart","Bar chart"),
            ("line","Line Chart","Line"),
            ("donut", "Donut Chart", "Donut Chart"),
            ("bubble", "Bubble Chart", "buble"),
            ("table", "Table", "Table"),
]

CSV_FORMATS = [("header","Header","Header"), ("left", "Left", "Left"), ("header-left","Header and Left", "Header and Left")]

BC_SHAPES = [("bar","Bar","Bar"),("cylinder","Cylinder","Cylinder"),("cone","Cone","Cone"),("pyramid","Pyramid","Pyramid")]

BC_SUB_TYPES = [("deep", "Deep", "Deep"),
                ("normal", "Normal", "Normal"),
                ("stacked", "Stacked", "Stacked"),
                ("percstacked", "Percent Stacked", "Percent Stacked"),
                ]

DONUT_SHAPES = [("cubic", "Cubic", "Cubic"), ("circle", "Circle", "Circle") ]

DATA_SERIES = [("columns","Columns", "Columns"), ("rows","Rows", "Rows"), ]

VALUE_COLOR = (1, 0.9, 0.7, 1)
LABEL_COLOR = (0.24, 0.45, 1, 1)
AXIS_COLOR = LABEL_COLOR
ROUGHNESS = 0.22
METALLIC = 1
ALPHA = 1