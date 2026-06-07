#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later

#set -euo pipefail


INPUT_DIR="${1:-.}"
OUTPUT_FILE="${2:-${INPUT_DIR}/blender_assets.cats.txt}"

CATALOG_DEFINITIONS="${CATALOG_MAP:-}"

UUID_TEMP=$(mktemp)
trap 'rm -f "$UUID_TEMP"' EXIT

read -r -d '' BLENDER_CATALOG_SCRIPT << 'PYTHON_SCRIPT'
import bpy
import json
import sys
import uuid

filepath = sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=filepath)

catalog_ids = set()
for id_block in bpy.data.user_map():
    if hasattr(id_block, 'asset_data') and id_block.asset_data:
        cat_id = id_block.asset_data.catalog_id
        if cat_id:
            catalog_ids.add(str(cat_id))

print("CATALOG_UUIDS:" + json.dumps(list(catalog_ids)))
PYTHON_SCRIPT

find "$INPUT_DIR" -type f -name "*.blend" | while read -r blend_path; do
    blender_output=$(blender --background --python-expr "$BLENDER_CATALOG_SCRIPT" -- "$blend_path" 2>/dev/null || true)
    uuids=$(echo "$blender_output" | grep '^CATALOG_UUIDS:' | sed 's/^CATALOG_UUIDS://' || echo '[]')

    python3 -c "
import json
for uid in json.loads('''$uuids'''):
    print(uid)
" >> "$UUID_TEMP"
done

unique_uuids=$(sort -u "$UUID_TEMP")

if [[ -z "$unique_uuids" ]]; then
    echo "Keine Katalog-IDs in .blend-Dateien gefunden." >&2
    exit 1
fi

declare -A CATALOG_PATHS
declare -A CATALOG_NAMES

if [[ -n "$CATALOG_DEFINITIONS" ]]; then
    IFS=';' read -ra DEFS <<< "$CATALOG_DEFINITIONS"
    for def in "${DEFS[@]}"; do
        [[ -z "$def" ]] && continue
        uid="${def%%:*}"
        path="${def#*:}"
        CATALOG_PATHS["$uid"]="$path"
        CATALOG_NAMES["$uid"]="${path##*/}"
    done
fi

{
    echo "# This is an Asset Catalog Definition file for Blender."
    echo "#"
    echo "# Empty lines and lines starting with # will be ignored."
    echo "# Each line should contain a UUID, a colon, and the catalog path."
    echo "#"
    echo "# For more information, see https://docs.blender.org/manual/en/latest/files/asset_libraries/catalogs.html"
    echo ""
    echo "VERSION 1"
    echo ""
} > "$OUTPUT_FILE"

echo "$unique_uuids" | while IFS= read -r uid; do
    [[ -z "$uid" ]] && continue

    if [[ -n "${CATALOG_PATHS[$uid]:-}" ]]; then
        path="${CATALOG_PATHS[$uid]}"
        name="${CATALOG_NAMES[$uid]}"
    else
        echo "Catalog ID with unknown path: $uid" >&2

        derived_path=$(find "$INPUT_DIR" -type f -name "*.blend" -exec blender --background --python-expr "
import bpy, sys, os
bpy.ops.wm.open_mainfile(filepath='{}')
for id_block in bpy.data.user_map():
    if hasattr(id_block, 'asset_data') and id_block.asset_data:
        if str(id_block.asset_data.catalog_id) == '$uid':
            # Pfad aus Dateipfad ableiten
            blend_dir = os.path.dirname('{}')
            rel_dir = os.path.relpath(blend_dir, '$INPUT_DIR')
            if rel_dir == '.':
                print('Uncategorized')
            else:
                print(rel_dir.replace(os.sep, '/'))
            break
" -- {} \; 2>/dev/null | grep -v '^Blender quit' | head -1 || true)

        if [[ -n "$derived_path" && "$derived_path" != "None" ]]; then
            path="$derived_path"
            name="${path##*/}"
            echo "  -> Derived from directory structure: $path" >&2
        else
            # Fallback: Interaktive Eingabe oder generischer Pfad
            if [[ -t 0 ]]; then
                read -rp "  Path for catalog $uid (e.g. 'Material/Metal'): " path
                name="${path##*/}"
            else
                path="Uncategorized/Import_${uid:0:8}"
                name="${path##*/}"
                echo "  -> Fallback path: $path" >&2
            fi
        fi

        CATALOG_PATHS["$uid"]="$path"
        CATALOG_NAMES["$uid"]="$name"
    fi

    echo "${uid}:${path}:${name}" >> "$OUTPUT_FILE"
done

echo "Generated: $OUTPUT_FILE"
echo "Entries: $(grep -c '^[0-9a-f]' "$OUTPUT_FILE" 2>/dev/null || echo 0)"
