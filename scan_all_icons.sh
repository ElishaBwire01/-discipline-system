#!/bin/bash

echo "==============================================="
echo "   COMPLETE ICON & EMOJI SCANNER"
echo "==============================================="
echo

DIRS="templates static"

for dir in $DIRS; do
    [ -d "$dir" ] || continue

    echo "==============================================="
    echo "Scanning: $dir"
    echo "==============================================="

    echo
    echo ">>> Unicode Emojis & Symbols"
    grep -RInP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' "$dir" 2>/dev/null

    echo
    echo ">>> Font Awesome Icons"
    grep -RInE 'fa[srlbd]?[[:space:]]+fa-[a-zA-Z0-9-]+' "$dir" 2>/dev/null

    echo
    echo ">>> Bootstrap Icons"
    grep -RInE 'bi[[:space:]]+bi-[a-zA-Z0-9-]+' "$dir" 2>/dev/null

    echo
    echo ">>> Material Icons"
    grep -RInE 'material-icons|material-symbols' "$dir" 2>/dev/null

    echo
    echo ">>> Ionicons"
    grep -RInE 'ion-|ionicon' "$dir" 2>/dev/null

    echo
    echo ">>> Feather Icons"
    grep -RInE 'data-feather=|feather[[:space:]]' "$dir" 2>/dev/null

    echo
    echo ">>> Heroicons"
    grep -RInE 'heroicon|heroicons' "$dir" 2>/dev/null

    echo
    echo ">>> Remix Icons"
    grep -RInE 'ri-[a-zA-Z0-9-]+' "$dir" 2>/dev/null

    echo
    echo ">>> Boxicons"
    grep -RInE 'bx[[:space:]]+bx-|bxs-|bxl-' "$dir" 2>/dev/null

    echo
    echo ">>> Tabler Icons"
    grep -RInE 'ti[[:space:]]+ti-|tabler-icon' "$dir" 2>/dev/null

    echo
    echo ">>> SVG Icons"
    grep -RIn "<svg|</svg>|<symbol|<use " "$dir" 2>/dev/null

    echo
    echo ">>> Image Icons (.png/.svg/.ico/.jpg/.webp)"
    find "$dir" -type f \( \
        -iname "*.svg" -o \
        -iname "*.png" -o \
        -iname "*.ico" -o \
        -iname "*.jpg" -o \
        -iname "*.jpeg" -o \
        -iname "*.webp" \
    \)

    echo
done

echo "==============================================="
echo "SCAN COMPLETE"
echo "==============================================="
