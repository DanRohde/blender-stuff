from bpy.types import PropertyGroup
from bpy.props import StringProperty, PointerProperty, CollectionProperty, EnumProperty, BoolProperty, IntProperty, BoolVectorProperty

from .handlers import handle_csv_filename_update

class CSVColumnTypeItems(PropertyGroup):
    name: StringProperty(name="", default="", description="Column label")
    column_type: EnumProperty(name="", items=[("float","Float","Float"),("label","Label","Label"),("date","Date","Date"),("int","Integer","Integer")], description="Column type")

class CSVProperties(PropertyGroup):
    csv_format: EnumProperty(name="Labels", items=[("header","Header","Header"), ("left", "Left", "Left"), ("header-left","Header and Left", "Header and Left")])
    column_types: CollectionProperty(type=CSVColumnTypeItems)
    column_types_idx: IntProperty()

class LegendProperties(PropertyGroup):
    enabled: BoolProperty(default=True, description="Enable/Disable legend")

def get_bc_sub_type(self, context):
    items = [("normal", "Normal", "Normal"), ("stacked", "Stacked", "Stacked")]
    if self.three_d_look: items.append(("deep", "Deep", "Deep"))
    return items

class ChartProperties(PropertyGroup):
    chart_type: EnumProperty(
        items=[
            ("column","Column Chart","Column chart"),
            ("bar","Bar Chart","Bar chart"),
            ("line","Line Chart","Line"),
            ("bubble", "Bubble Chart", "buble")],
        name="Type", description="Chart type")
    axes: BoolVectorProperty(name="Axes", size=3, description="XYZ Axes")
    legend_properties: PointerProperty(type=LegendProperties)
    # bar, column charts:
    three_d_look: BoolProperty(default=True, name="3D Look", description="3D Look")
    three_d_shape: EnumProperty(items=[("bar","Bar","Bar"),("cylinder","Cylinder","Cylinder"),("cone","Cone","Cone"),("pyramid","Pyramid","Pyramid")], name="Shape", description="Shape")
    bc_sub_type: EnumProperty(items=get_bc_sub_type, name="Subtype", description="Subtype")

class Properties(PropertyGroup):
    csv_filename: StringProperty(default="", subtype="FILE_PATH", name="CSV File", description="CSV File", update=handle_csv_filename_update)
    csv_properties: PointerProperty(type=CSVProperties)
    column_types_collapsed: BoolProperty(name="Column Types", default=True)
    chart_properties: PointerProperty(type=ChartProperties)

properties = [ LegendProperties, ChartProperties, CSVColumnTypeItems, CSVProperties, Properties ]


