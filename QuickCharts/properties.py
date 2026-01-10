from bpy.types import PropertyGroup
from bpy.props import StringProperty, PointerProperty, CollectionProperty, EnumProperty, BoolProperty, IntProperty, BoolVectorProperty, FloatVectorProperty

from .handlers import handle_csv_filename_update

from .constants import CHART_TYPES, CSV_FORMATS, BC_SHAPES, BC_SUB_TYPES, DATA_SERIES

class CSVColumnTypeItems(PropertyGroup):
    name: StringProperty(name="", default="", description="Column label")
    column_type: EnumProperty(name="", items=[("float","Float","Float"),("label","Label","Label"), ("int","Integer","Integer")], description="Column type")

class CSVProperties(PropertyGroup):
    csv_format: EnumProperty(name="Labels", items=CSV_FORMATS)
    column_types: CollectionProperty(type=CSVColumnTypeItems)
    column_types_idx: IntProperty()

class LegendProperties(PropertyGroup):
    enabled: BoolProperty(default=True, name="Legend", description="Enable/Disable legend")

class ChartProperties(PropertyGroup):
    chart_type: EnumProperty(items=CHART_TYPES, name="Type", description="Chart type")
    legend_properties: PointerProperty(type=LegendProperties)
    # bar, column charts:
    bc_shape: EnumProperty(items=BC_SHAPES, name="Shape", description="Shape")
    bc_sub_type: EnumProperty(items=BC_SUB_TYPES, name="Subtype", description="Subtype")

    data_series: EnumProperty(items=DATA_SERIES, name="Data series", description="Data series")

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


