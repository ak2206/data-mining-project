#!/bin/bash
# Converts all files in the FILES_TO_WORK directory to kml
# leaving them in the directory KML_FILES_TO_WORK
for file in FILES_TO_WORK/*.txt; do
    python gsi_to_kml.py "$file" > /dev/null 2>&1
    # This just assumes that KML_FILES_TO_WORK exists
    cp foo.kml "KML_${file/%.txt/.kml}"
    rm foo.kml
done