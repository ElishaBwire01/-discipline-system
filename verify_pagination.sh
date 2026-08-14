#!/bin/bash

FILE="core/views.py"

echo "========================================"
echo "VERIFYING DJANGO PAGINATION CONNECTION"
echo "========================================"

echo
echo ">>> Paginator creation"
grep -n "Paginator(" "$FILE"

echo
echo ">>> students_page assignment"
grep -n "students_page" "$FILE"

echo
echo ">>> page_obj assignment"
grep -n '"page_obj"' "$FILE"

echo
echo ">>> students assignment"
grep -nE "^[[:space:]]*students[[:space:]]*=" "$FILE"

echo
echo ">>> Context blocks around page_obj"
for line in $(grep -n '"page_obj"' "$FILE" | cut -d: -f1); do
    start=$((line-10))
    end=$((line+10))
    [ "$start" -lt 1 ] && start=1
    echo
    echo "---------- Lines $start-$end ----------"
    sed -n "${start},${end}p" "$FILE"
done

echo
echo ">>> Context around students_page"
for line in $(grep -n "students_page" "$FILE" | cut -d: -f1); do
    start=$((line-10))
    end=$((line+15))
    [ "$start" -lt 1 ] && start=1
    echo
    echo "---------- Lines $start-$end ----------"
    sed -n "${start},${end}p" "$FILE"
done

echo
echo "========================================"
echo "Verification complete."
