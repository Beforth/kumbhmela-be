#!/bin/bash
# Script to import all KMZ files from kmz-files directory

cd "$(dirname "$0")"
source venv/bin/activate

KMZ_DIR="kmz-files"

if [ ! -d "$KMZ_DIR" ]; then
    echo "Error: $KMZ_DIR directory not found"
    exit 1
fi

echo "Importing KMZ files from $KMZ_DIR..."
echo ""

for kmz_file in "$KMZ_DIR"/*.kmz; do
    if [ -f "$kmz_file" ]; then
        filename=$(basename "$kmz_file")
        echo "Processing: $filename"
        
        # Auto-detect feature type from filename
        feature_type="other"
        if [[ "$filename" == *"Road"* ]] || [[ "$filename" == *"route"* ]]; then
            feature_type="road"
        elif [[ "$filename" == *"parking"* ]] || [[ "$filename" == *"Parking"* ]]; then
            feature_type="parking"
        elif [[ "$filename" == *"Holding"* ]] || [[ "$filename" == *"holding"* ]]; then
            feature_type="holding_area"
        elif [[ "$filename" == *"Staging"* ]] || [[ "$filename" == *"staging"* ]]; then
            feature_type="staging_area"
        elif [[ "$filename" == *"release"* ]] || [[ "$filename" == *"Release"* ]]; then
            feature_type="release_point"
        elif [[ "$filename" == *"Inner"* ]] || [[ "$filename" == *"Outer"* ]] || [[ "$filename" == *"Zone"* ]]; then
            feature_type="zone"
        elif [[ "$filename" == *"Area"* ]] || [[ "$filename" == *"area"* ]]; then
            feature_type="area"
        fi
        
        python manage.py import_kmz "$kmz_file" --feature-type="$feature_type" --clear-existing
        echo ""
    fi
done

echo "Done importing all KMZ files!"

