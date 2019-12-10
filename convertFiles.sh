#!/bin/bash
# Converts all files in the FILES_TO_WORK directory to kml
# leaving them in the directory KML_FILES_TO_WORK
mkdir -p KML_FILES_TO_WORK
for file in FILES_TO_WORK/*.txt; do
    python3 gsi_to_kml.py "$file" > /dev/null 2>&1
    cp foo.kml "KML_${file/%.txt/.kml}"
done
rm foo.kml