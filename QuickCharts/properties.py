from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty, EnumProperty, BoolProperty, IntProperty, FloatVectorProperty, FloatProperty

from .handlers import handle_csv_filename_update, handle_data_series_update

from .constants import CHART_TYPES, CSV_FORMATS, BC_SHAPES, BC_SUB_TYPES, DATA_SERIES, ROUGHNESS, METALLIC, ALPHA, ICONS, DONUT_SHAPES
from .icons import preview_collections


def get_enum_items(consts, prefix):
    items = []
    pcoll = preview_collections["main"]
    for idx, ct in enumerate(consts):
        id = f"{ct[0]}_{prefix}"
        if id in ICONS:
            items.append((ct[0], ct[1], ct[2], pcoll[id].icon_id, idx))
        else:
            items.append(ct)
    return items

def get_chart_types_enum_items(_self, _context):
    return get_enum_items(CHART_TYPES, "chart")

def get_csv_format_enum_items(_self, _context):
    return get_enum_items(CSV_FORMATS, "label")

def get_bc_shapes_enum_items(_self, _context):
    return get_enum_items(BC_SHAPES, "shape")

def get_bc_sub_types_enum_items(_self, _context):
    return get_enum_items(BC_SUB_TYPES, "subtype")

def get_data_series_enum_items(_self, _context):
    return get_enum_items(DATA_SERIES, "series")

class CSVCellTypeItems(PropertyGroup):
    name: StringProperty(name="", default="", description="Column label")
    cell_type: EnumProperty(name="", items=[("float","Float","Float"),("label","Label","Label"), ("int","Integer","Integer")], description="Column type")
    precision: IntProperty(default=1, min=0, name="", description="Precision")

class Properties(PropertyGroup):
    # CSV:
    csv_filename: StringProperty(default="", subtype="FILE_PATH", name="CSV File", description="CSV File", update=handle_csv_filename_update)
    csv_format: EnumProperty(name="Labels", items=get_csv_format_enum_items)
    cell_types: CollectionProperty(type=CSVCellTypeItems)
    cell_types_idx: IntProperty()
    cell_types_collapsed: BoolProperty(name="Cell Types", default=True)


    material_collapsed: BoolProperty(name="Material", default=True)

    # Chart:
    chart_type: EnumProperty(items=get_chart_types_enum_items, name="", description="Chart type")
    # bar, column charts:
    bc_shape: EnumProperty(items=get_bc_shapes_enum_items, name="", description="Shape")
    bc_sub_type: EnumProperty(items=get_bc_sub_types_enum_items, name="", description="Subtype")
    # donat charts:
    donut_shape: EnumProperty(items=DONUT_SHAPES, name="Shape", description="Shape")

    data_series: EnumProperty(items=get_data_series_enum_items, name="", description="Data series", update=handle_data_series_update)

    size: FloatVectorProperty(name="Size", size=3, description="Chart size", default=(10, 10, 10), subtype="XYZ_LENGTH")
    spacing: FloatVectorProperty(name="Spacing", size=3, subtype="XYZ_LENGTH", default=(0.1, 0.1, 0.1), min=0)

    legend: BoolProperty(default=True, name="Legend", description="Show legend")
    labels: BoolProperty(default=True, name="Labels", description="Show labels")
    values: BoolProperty(default=True, name="Values", description="Show values")
    axis: BoolProperty(default=True, name="Axis", description="Show axis")

    label_color: FloatVectorProperty(name="Label Color", description="Label color", size=4, subtype="COLOR", default=(0.24, 0.45, 1, 1), min=0, max=1)
    label_roughness: FloatProperty(default=ROUGHNESS, name="Label Roughness", description="Label Roughness", min=0, max=1)
    label_metallic: FloatProperty(default=METALLIC, name="Label Metallic", description="Label Metallic", min=0, max=1)

    value_color: FloatVectorProperty(name="Value Color", description="Value color", size=4, subtype="COLOR", default=(1, 0.9, 0.7, 1), min=0, max=1)
    value_roughness: FloatProperty(default=ROUGHNESS, name="Value Roughness", description="Value Roughness", min=0, max=1)
    value_metallic: FloatProperty(default=METALLIC, name="Value Metallic", description="Value Metallic", min=0, max=1)


    roughness: FloatProperty(default=ROUGHNESS, name="Roughness", description="Chart Roughness", min=0, max=1)
    metallic: FloatProperty(default=METALLIC, name="Metallic", description="Chart Metallic", min=0, max=1)
    alpha: FloatProperty(default=ALPHA, name="Alpha", description="Chart Alpha", min=0, max=1)
properties = [ CSVCellTypeItems, Properties ]

