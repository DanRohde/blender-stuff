from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty, EnumProperty, BoolProperty, IntProperty, FloatVectorProperty, FloatProperty

from .handlers import handle_csv_filename_update

from .constants import CHART_TYPES, CSV_FORMATS, BC_SHAPES, BC_SUB_TYPES, DATA_SERIES, ROUGHNESS, METALLIC, ALPHA, ICONS
from .icons import preview_collections


def get_enum_items(consts, prefix):
    items = []
    pcoll = preview_collections["main"]
    for idx, ct in enumerate(consts):
        items.append((ct[0], ct[1], ct[2], pcoll[f"{ct[0]}_{prefix}"].icon_id, idx))
    return items

def get_chart_types_enum_items(_self, _context):
    return get_enum_items(CHART_TYPES, "chart")

def get_csv_format_enum_items(_self, _context):
    return get_enum_items(CSV_FORMATS, "label")

class CSVColumnTypeItems(PropertyGroup):
    name: StringProperty(name="", default="", description="Column label")
    column_type: EnumProperty(name="", items=[("float","Float","Float"),("label","Label","Label"), ("int","Integer","Integer")], description="Column type")
    precision: IntProperty(default=1, min=0, name="", description="Precision")

class Properties(PropertyGroup):
    # CSV:
    csv_filename: StringProperty(default="", subtype="FILE_PATH", name="CSV File", description="CSV File", update=handle_csv_filename_update)
    csv_format: EnumProperty(name="Labels", items=get_csv_format_enum_items)
    column_types: CollectionProperty(type=CSVColumnTypeItems)
    column_types_idx: IntProperty()
    column_types_collapsed: BoolProperty(name="Column Types", default=True)

    # Chart:
    chart_type: EnumProperty(items=get_chart_types_enum_items, name="Chart", description="Chart type")
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
    label_roughness: FloatProperty(default=ROUGHNESS, name="Label/Value Roughness", description="Label/Value Roughness", min=0, max=1)
    label_metallic: FloatProperty(default=METALLIC, name="Label/Value Metallic", description="Label/Value Metallic", min=0, max=1)

    roughness: FloatProperty(default=ROUGHNESS, name="Roughness", description="Chart Roughness", min=0, max=1)
    metallic: FloatProperty(default=METALLIC, name="Metallic", description="Chart Metallic", min=0, max=1)
    alpha: FloatProperty(default=ALPHA, name="Alpha", description="Chart Alpha", min=0, max=1)
properties = [ CSVColumnTypeItems, Properties ]


