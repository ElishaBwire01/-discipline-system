#!/bin/bash

TEMPLATES_DIR="templates"

if [ ! -d "$TEMPLATES_DIR" ]; then
    echo "Error: '$TEMPLATES_DIR' directory not found."
    exit 1
fi

echo "==============================================="
echo "      DJANGO TEMPLATE EMOJI SCANNER"
echo "==============================================="
echo

echo "Templates scanned:"
find "$TEMPLATES_DIR" -type f \( -name "*.html" -o -name "*.htm" \) | wc -l
echo

echo "-----------------------------------------------"
echo "EMOJIS FOUND (with occurrence count)"
echo "-----------------------------------------------"

find "$TEMPLATES_DIR" -type f \( -name "*.html" -o -name "*.htm" \) -print0 |
xargs -0 cat |
grep -oP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' |
sort |
uniq -c |
sort -nr

echo
echo "-----------------------------------------------"
echo "FILES CONTAINING EMOJIS"
echo "-----------------------------------------------"

find "$TEMPLATES_DIR" -type f \( -name "*.html" -o -name "*.htm" \) | while read -r file
do
    if grep -qP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' "$file"; then
        echo
        echo "File: $file"
        echo "-------------------------------------------"
        grep -nP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' "$file"
    fi
done

echo
echo "==============================================="
echo "SCAN COMPLETE"
echo "==============================================="
