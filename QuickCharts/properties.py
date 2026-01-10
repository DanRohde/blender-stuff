from bpy.types import PropertyGroup
from bpy.props import StringProperty, PointerProperty, CollectionProperty, EnumProperty, BoolProperty, IntProperty, BoolVectorProperty, FloatVectorProperty

from .handlers import handle_csv_filename_update

class CSVColumnTypeItems(PropertyGroup):
    name: StringProperty(name="", default="", description="Column label")
    column_type: EnumProperty(name="", items=[("float","Float","Float"),("label","Label","Label"), ("int","Integer","Integer")], description="Column type")

class CSVProperties(PropertyGroup):
    csv_format: EnumProperty(name="Labels", items=[("header","Header","Header"), ("left", "Left", "Left"), ("header-left","Header and Left", "Header and Left")])
    column_types: CollectionProperty(type=CSVColumnTypeItems)
    column_types_idx: IntProperty()

class LegendProperties(PropertyGroup):
    enabled: BoolProperty(default=True, name="Legend", description="Enable/Disable legend")

def get_bc_sub_type(self, context):
    items = [("normal", "Normal", "Normal"), ("stacked", "Stacked", "Stacked"),("deep", "Deep", "Deep")]
    return items

class ChartProperties(PropertyGroup):
    chart_type: EnumProperty(
        items=[
            ("column","Column Chart","Column chart"),
            ("bar","Bar Chart","Bar chart"),
            ("line","Line Chart","Line"),
            ("pie","Pie Chart","Pie"),
            ("donut", "Donut Chart", "Donut Chart"),
            # ("bubble", "Bubble Chart", "buble")
        ],
        name="Type", description="Chart type")
    legend_properties: PointerProperty(type=LegendProperties)
    # bar, column charts:
    three_d_shape: EnumProperty(items=[("bar","Bar","Bar"),("cylinder","Cylinder","Cylinder"),("cone","Cone","Cone"),("pyramid","Pyramid","Pyramid")], name="Shape", description="Shape")
    bc_sub_type: EnumProperty(items=get_bc_sub_type, name="Subtype", description="Subtype")

    data_series: EnumProperty(items=[("columns","Columns", "Columns"), ("rows","Rows", "Rows"), ], name="Data series", description="Data series")

    size: FloatVectorProperty(name="Chart Size", size=3, description="Chart size", default=(10,10,10), subtype="XYZ_LENGTH")
    spacing: FloatVectorProperty(name="Chart Spacing", size=3, subtype="XYZ_LENGTH", default=(0.1,0.1,0.1))
    min_xyz: FloatVectorProperty(size=3)
    max_xyz: FloatVectorProperty(size=3)

class Properties(PropertyGroup):
    csv_filename: StringProperty(default="", subtype="FILE_PATH", name="CSV File", description="CSV File", update=handle_csv_filename_update)
    csv_properties: PointerProperty(type=CSVProperties)
    column_types_collapsed: BoolProperty(name="Column Types", default=True)
    chart_properties: PointerProperty(type=ChartProperties)

properties = [ LegendProperties, ChartProperties, CSVColumnTypeItems, CSVProperties, Properties ]


