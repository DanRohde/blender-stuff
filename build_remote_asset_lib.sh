#!/usr/bin/env bash

#set -euo pipefail

LIBRARY_NAME="DanRohde's Blender Remote Asset Library"
CONTACT_NAME="DanRohde"
CONTACT_URL="https://github.com/DanRohde/blender-stuff"
CONTACT_EMAIL="d.rohde@web.de"

SCHEMA_VERSION="1.0.0"
API_VERSION="v1"
ASSETS_PER_PAGE=100

INPUT_DIR="${1:-.}"
OUTPUT_DIR="${2:-./_v1}"
THUMBNAIL_SUFFIX="_thumb.webp"

echo Create output dir $OUTPUT_DIR
mkdir -p "$OUTPUT_DIR"

ASSETS_TEMP=$(mktemp)
FILES_TEMP=$(mktemp)
CATALOGS_TEMP=$(mktemp)
CATALOG_MAP=$(mktemp)
trap 'rm -f "$ASSETS_TEMP" "$FILES_TEMP" "$CATALOGS_TEMP" "$CATALOG_MAP"' EXIT

TOTAL_ASSET_SIZE=0
TOTAL_ASSET_COUNT=0
TOTAL_FILE_COUNT=0

sha256_file() {
    sha256sum "$1" | awk '{print $1}'
}

json_escape() {
    printf '%s' "$1" | sed 's/["\\]/\\&/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

url_with_hash() {
    local url="$1"
    local file="$2"
    local hash
    hash=$(sha256_file "$file")
    printf '{"url": "%s", "hash": "SHA256:%s"}' "$url" "$hash"
}

# Blender-Python-Skript zur Asset-Extraktion
read -r -d '' BLENDER_EXTRACT_SCRIPT << 'PYTHON_SCRIPT'
import bpy
import json
import sys
import os

filepath = sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=filepath)

result = {
    "version": ".".join(str(v) for v in bpy.app.version[:2]),
    "assets": []
}

for id_block in bpy.data.user_map():
    if not hasattr(id_block, 'asset_data') or id_block.asset_data is None:
        continue

    meta = id_block.asset_data

    asset_info = {
        "name": id_block.name,
        "id_type": id_block.id_type,
        "catalog_id": str(meta.catalog_id) if meta.catalog_id else "",
        "catalog_path": "",
        "tags": [tag.name for tag in meta.tags],
        "author": meta.author or "",
        "description": meta.description or "",
        "license": meta.license or "",
        "copyright": meta.copyright or "",
        "preferred_import_method": getattr(meta, 'preferred_import_method', '') or ""
    }

    # Katalog-Pfad aus .cats.txt auflösen
    if meta.catalog_id:
        for catalog in bpy.context.preferences.filepaths.asset_libraries:
            cats_path = os.path.join(os.path.dirname(catalog.path), "blender_assets.cats.txt")
            if os.path.exists(cats_path):
                with open(cats_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('#') or not line:
                            continue
                        parts = line.split(':')
                        if len(parts) >= 3 and parts[0] == str(meta.catalog_id):
                            asset_info["catalog_path"] = parts[1]
                            break

    result["assets"].append(asset_info)

print("BLENDER_ASSET_DATA:" + json.dumps(result))
PYTHON_SCRIPT

# Alle .blend-Dateien finden und verarbeiten
declare -A PROCESSED_FILES

find "$INPUT_DIR" -type f -name "*.blend" | sort | while read -r blend_path; do
    rel_path="${blend_path#$INPUT_DIR/}"
    rel_path="${rel_path#./}"

    # Thumbnail-Pfad ableiten
    thumb_base="${blend_path%.blend}"
    thumbnail_path="${thumb_base}${THUMBNAIL_SUFFIX}"

    # Fallback: Thumbnail neben .blend mit anderem Namungsschema
    if [[ ! -f "$thumbnail_path" ]]; then
        thumbnail_path="${INPUT_DIR}/thumbnails/$(basename "${rel_path%.blend}").webp"
    fi

    # extract Blender version and asset data
    blender_output=$(blender --background --python-expr "$BLENDER_EXTRACT_SCRIPT" -- "$blend_path" 2>/dev/null || true)
    asset_data=$(echo "$blender_output" | grep '^BLENDER_ASSET_DATA:' | sed 's/^BLENDER_ASSET_DATA://' || echo '{"version":"0.0","assets":[]}')

    bl_version=$(echo "$asset_data" | python3 -c "import sys,json; print(json.load(sys.stdin)['version'])")

    # file information
    file_size=$(stat -c%s "$blend_path" 2>/dev/null || stat -f%z "$blend_path")
    file_hash=$(sha256_file "$blend_path")

    #  file JSON (only one per .blend)
    if [[ -z "${PROCESSED_FILES[$rel_path]:-}" ]]; then
        {
            printf '    {\n'
            printf '      "path": "%s",\n' "$(json_escape "$rel_path")"
            printf '      "url": "files/%s",\n' "$(json_escape "$rel_path")"
            printf '      "size_in_bytes": %d,\n' "$file_size"
            printf '      "hash": "SHA256:%s",\n' "$file_hash"
            printf '      "blender_version": "%s"\n' "$bl_version"
            printf '    }'
        } >> "$FILES_TEMP"
        printf ',\n' >> "$FILES_TEMP"
        PROCESSED_FILES["$rel_path"]=1
        ((TOTAL_FILE_COUNT++)) || true
        ((TOTAL_ASSET_SIZE += file_size)) || true
    fi

    # calculate Thumbnail hash
    thumb_json="null"
    if [[ -f "$thumbnail_path" ]]; then
        thumb_rel="${thumbnail_path#$INPUT_DIR/}"
        thumb_rel="${thumb_rel#./}"
        thumb_json=$(url_with_hash "$thumb_rel" "$thumbnail_path")
    fi

    # Assets aus dieser .blend-Datei verarbeiten
    python3 -c "
import sys, json

data = json.loads('''$asset_data''')
thumb_json = '''$thumb_json'''
rel_path = '''$rel_path'''

for asset in data['assets']:
    # Katalog verfolgen
    catalog_path = asset.get('catalog_path', '') or 'Uncategorized'
    catalog_id = asset.get('catalog_id', '') or ''

    # Asset-JSON ausgeben
    print('ASSET_START')
    print(json.dumps({
        'name': asset['name'],
        'id_type': asset['id_type'],
        'files': [rel_path],
        'thumbnail': json.loads(thumb_json) if thumb_json != 'null' else None,
        'meta': {k: v for k, v in {
            'catalog_id': catalog_id,
            'preferred_import_method': asset.get('preferred_import_method') or None,
            'tags': asset['tags'] if asset['tags'] else None,
            'author': asset['author'] or None,
            'description': asset['description'] or None,
            'license': asset['license'] or None,
            'copyright': asset['copyright'] or None
        }.items() if v is not None},
        'bl_versions': {'min': data['version']}
    }, ensure_ascii=False))
    print('CATALOG:' + catalog_path + ':' + catalog_id)
    print('ASSET_END')
" | while IFS= read -r line; do
        case "$line" in
            ASSET_START)
                read -r asset_json
                printf '%s' "$asset_json" | python3 -c "
import sys, json
asset = json.load(sys.stdin)
print('    ' + json.dumps(asset, indent=2, ensure_ascii=False).replace('\n', '\n    '))
" >> "$ASSETS_TEMP"
                printf ',\n' >> "$ASSETS_TEMP"
                ((TOTAL_ASSET_COUNT++)) || true
                ;;
            CATALOG:*)
                catalog_path="${line#CATALOG:}"
                catalog_id="${catalog_path##*:}"
                catalog_path="${catalog_path%:*}"
                if [[ -n "$catalog_path" && -n "$catalog_id" ]]; then
                    printf '%s\0%s\n' "$catalog_path" "$catalog_id" >> "$CATALOG_MAP"
                fi
                ;;
        esac
    done
done

# Letztes Komma entfernen
[[ -s "$ASSETS_TEMP" ]] && sed -i '$ s/,\s*$//' "$ASSETS_TEMP"
[[ -s "$FILES_TEMP" ]] && sed -i '$ s/,\s*$//' "$FILES_TEMP"

# Kataloge deduplizieren und formatieren
if [[ -s "$CATALOG_MAP" ]]; then
    sort -zu "$CATALOG_MAP" | uniq -z | while IFS= read -r -d '' line; do
        catalog_path="${line%$'\0'*}"
        catalog_id="${line#*$'\0'}"
        simple_name="${catalog_path##*/}"
        {
            printf '    {\n'
            printf '      "path": "%s",\n' "$(json_escape "$catalog_path")"
            printf '      "simple_name": "%s",\n' "$(json_escape "$simple_name")"
            printf '      "uuids": ["%s"]\n' "$catalog_id"
            printf '    }'
        } >> "$CATALOGS_TEMP"
        printf ',\n' >> "$CATALOGS_TEMP"
    done
    sed -i '$ s/,\s*$//' "$CATALOGS_TEMP"
fi

# Fallback-Katalog falls leer
if [[ ! -s "$CATALOGS_TEMP" ]]; then
    printf '    {\n      "path": "Uncategorized",\n      "simple_name": "Uncategorized",\n      "uuids": ["00000000-0000-0000-0000-000000000000"]\n    }' >> "$CATALOGS_TEMP"
fi

# Seiten generieren
PAGE_FILE="$OUTPUT_DIR/assets-1.json"
{
    printf '{\n'
    printf '  "asset_count": %d,\n' "$TOTAL_ASSET_COUNT"
    printf '  "file_count": %d,\n' "$TOTAL_FILE_COUNT"
    printf '  "assets": [\n'
    [[ -s "$ASSETS_TEMP" ]] && cat "$ASSETS_TEMP"
    printf '\n  ],\n'
    printf '  "files": [\n'
    [[ -s "$FILES_TEMP" ]] && cat "$FILES_TEMP"
    printf '\n  ]\n'
    printf '}\n'
} > "$PAGE_FILE"

PAGE_HASH=$(sha256_file "$PAGE_FILE")

# Index-JSON
INDEX_FILE="$OUTPUT_DIR/asset-index.json"
{
    printf '{\n'
    printf '  "schema_version": "%s",\n' "$SCHEMA_VERSION"
    printf '  "asset_size_bytes": %d,\n' "$TOTAL_ASSET_SIZE"
    printf '  "asset_count": %d,\n' "$TOTAL_ASSET_COUNT"
    printf '  "file_count": %d,\n' "$TOTAL_FILE_COUNT"
    printf '  "pages": [\n'
    printf '    {\n'
    printf '      "url": "%s",\n' "_${API_VERSION}/assets-1.json"
    printf '      "hash": "SHA256:%s"\n' "$PAGE_HASH"
    printf '    }\n'
    printf '  ],\n'
    printf '  "catalogs": [\n'
    cat "$CATALOGS_TEMP"
    printf '\n  ]\n'
    printf '}\n'
} > "$INDEX_FILE"

INDEX_HASH=$(sha256_file "$INDEX_FILE")

# Meta-JSON
META_FILE="_asset-library-meta.json"
{
    printf '{\n'
    printf '  "api_versions": {\n'
    printf '    "%s": {\n' "$API_VERSION"
    printf '      "url": "%s",\n' "_${API_VERSION}/asset-index.json"
    printf '      "hash": "SHA256:%s"\n' "$INDEX_HASH"
    printf '    }\n'
    printf '  },\n'
    printf '  "name": "%s",\n' "$(json_escape "$LIBRARY_NAME")"
    printf '  "contact": {\n'
    printf '    "name": "%s"' "$(json_escape "$CONTACT_NAME")"
    [[ -n "$CONTACT_URL" ]] && printf ',\n    "url": "%s"' "$(json_escape "$CONTACT_URL")"
    [[ -n "$CONTACT_EMAIL" ]] && printf ',\n    "email": "%s"' "$(json_escape "$CONTACT_EMAIL")"
    printf '\n  }\n'
    printf '}\n'
} > "$META_FILE"

echo "Generated: $META_FILE, $INDEX_FILE, $PAGE_FILE"
echo "Assets: $TOTAL_ASSET_COUNT, Files: $TOTAL_FILE_COUNT, Total size: $TOTAL_ASSET_SIZE Bytes"
