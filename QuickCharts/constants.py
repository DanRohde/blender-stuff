COLORS = [
    (1,0,0,1),
    (0,1,0,1),
    (0,0,1,1),
    (1,0,1,1),
    (1,1,0,1),
    (1,1,1,1),
    (0,1,1,1),
    (0,0,0,1)
]


ICONS = {
    "header_label" : "labels_header.png",
    "header-left_label" : "labels_header_left.png",
    "left_label" :  "labels_left.png",
    "data_series_columns" : "data_series_columns.png",
    "data_series_rows" : "data_series_rows.png",
    "column_chart" : "column_chart.png",
    "bar_chart" : "bar_chart.png",
    "bc_subtype_deep" : "bc_subtype_deep.png",
    "bc_subtype_stacked" : "bc_subtype_stacked.png",
    "bc_subtype_percstacked" : "bc_subtype_percstacked.png",
    "bc_subtype_normal" : "bc_subtype_normal.png",
    "bc_shape_bar" : "bc_shape_bar.png",
    "bc_shape_cylinder" : "bc_shape_cylinder.png",
    "bc_shape_cone" : "bc_shape_cone.png",
    "bc_shape_pyramid" : "bc_shape_pyramind.png",
}

CHART_TYPES = [
            ("column","Column Chart","Column chart"),
            ("bar","Bar Chart","Bar chart"),
            #("line","Line Chart","Line"),
            #("pie","Pie Chart","Pie"),
            #("donut", "Donut Chart", "Donut Chart"),
            # ("bubble", "Bubble Chart", "buble")
        ]

CSV_FORMATS = [("header","Header","Header"), ("left", "Left", "Left"), ("header-left","Header and Left", "Header and Left")]

BC_SHAPES = [("bar","Bar","Bar"),("cylinder","Cylinder","Cylinder"),("cone","Cone","Cone"),("pyramid","Pyramid","Pyramid")]

BC_SUB_TYPES = [("normal", "Normal", "Normal"),
                ("stacked", "Stacked", "Stacked"),
                ("percstacked", "Percent Stacked", "Percent Stacked"),
                ("deep", "Deep", "Deep")]

DATA_SERIES = [("columns","Columns", "Columns"), ("rows","Rows", "Rows"), ]

ROUGHNESS = 0.22
METALLIC = 1
ALPHA = 1