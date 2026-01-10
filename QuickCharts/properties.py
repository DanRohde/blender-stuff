from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty, EnumProperty, BoolProperty, IntProperty, FloatVectorProperty, FloatProperty

from .handlers import handle_csv_filename_update

from .constants import CHART_TYPES, CSV_FORMATS, BC_SHAPES, BC_SUB_TYPES, DATA_SERIES, ROUGHNESS, METALLIC, ALPHA

class CSVColumnTypeItems(PropertyGroup):
    name: StringProperty(name="", default="", description="Column label")
    column_type: EnumProperty(name="", items=[("float","Float","Float"),("label","Label","Label"), ("int","Integer","Integer")], description="Column type")

class Properties(PropertyGroup):
    # CSV:
    csv_filename: StringProperty(default="", subtype="FILE_PATH", name="CSV File", description="CSV File", update=handle_csv_filename_update)
    csv_format: EnumProperty(name="Labels", items=CSV_FORMATS)
    column_types: CollectionProperty(type=CSVColumnTypeItems)
    column_types_idx: IntProperty()
    column_types_collapsed: BoolProperty(name="Column Types", default=True)

    # Chart:
    chart_type: EnumProperty(items=CHART_TYPES, name="Type", description="Chart type")
    # bar, column charts:
    bc_shape: EnumProperty(items=BC_SHAPES, name="Shape", description="Shape")
    bc_sub_type: EnumProperty(items=BC_SUB_TYPES, name="Subtype", description="Subtype")

    data_series: EnumProperty(items=DATA_SERIES, name="Data series", description="Data series")

    size: FloatVectorProperty(name="Size", size=3, description="Chart size", default=(10, 10, 10), subtype="XYZ_LENGTH")
    spacing: FloatVectorProperty(name="Spacing", size=3, subtype="XYZ_LENGTH", default=(0.1, 0.1, 0.1))

    legend: BoolProperty(default=True, name="Legend", description="Enable/Disable legend")
    labels: BoolProperty(default=True, name="Labels", description="Enable/Disable labels")
    values: BoolProperty(default=True, name="Values", description="Enable/Disable values")

    label_color: FloatVectorProperty(name="Label/Value Color", description="Label/Value color", size=4, subtype="COLOR", default=(1, 1, 1, 1), min=0, max=1)

    roughness: FloatProperty(default=ROUGHNESS, name="Roughness", description="Roughness", min=0, max=1)
    metallic: FloatProperty(default=METALLIC, name="Metallic", description="Metallic", min=0, max=1)
    alpha: FloatProperty(default=ALPHA, name="Alpha", description="Alpha", min=0, max=1)
properties = [ CSVColumnTypeItems, Properties ]


