#!/bin/bash

echo "==============================================="
echo "   COMPLETE ICON & EMOJI COUNTER"
echo "==============================================="
echo

DIRS="templates static"

# Initialize counters
TOTAL_EMOJIS=0
TOTAL_FA=0
TOTAL_BI=0
TOTAL_MATERIAL=0
TOTAL_ION=0
TOTAL_FEATHER=0
TOTAL_HERO=0
TOTAL_REMIX=0
TOTAL_BOX=0
TOTAL_TABLER=0
TOTAL_SVG=0
TOTAL_IMAGE_FILES=0

echo "==============================================="
echo "COUNTING ICONS AND EMOJIS"
echo "==============================================="
echo

for dir in $DIRS; do
    [ -d "$dir" ] || continue

    echo "📁 Scanning: $dir"
    echo "-----------------------------------------------"

    # Unicode Emojis & Symbols
    EMOJI_COUNT=$(grep -RInP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]' "$dir" 2>/dev/null | wc -l)
    TOTAL_EMOJIS=$((TOTAL_EMOJIS + EMOJI_COUNT))
    echo "  🔤 Unicode Emojis: $EMOJI_COUNT"

    # Font Awesome Icons
    FA_COUNT=$(grep -RInE 'fa[srlbd]?[[:space:]]+fa-[a-zA-Z0-9-]+' "$dir" 2>/dev/null | wc -l)
    TOTAL_FA=$((TOTAL_FA + FA_COUNT))
    echo "  🎨 Font Awesome: $FA_COUNT"

    # Bootstrap Icons
    BI_COUNT=$(grep -RInE 'bi[[:space:]]+bi-[a-zA-Z0-9-]+' "$dir" 2>/dev/null | wc -l)
    TOTAL_BI=$((TOTAL_BI + BI_COUNT))
    echo "  🅱️ Bootstrap Icons: $BI_COUNT"

    # Material Icons
    MATERIAL_COUNT=$(grep -RInE 'material-icons|material-symbols' "$dir" 2>/dev/null | wc -l)
    TOTAL_MATERIAL=$((TOTAL_MATERIAL + MATERIAL_COUNT))
    echo "  📐 Material Icons: $MATERIAL_COUNT"

    # Ionicons
    ION_COUNT=$(grep -RInE 'ion-|ionicon' "$dir" 2>/dev/null | wc -l)
    TOTAL_ION=$((TOTAL_ION + ION_COUNT))
    echo "  ⚡ Ionicons: $ION_COUNT"

    # Feather Icons
    FEATHER_COUNT=$(grep -RInE 'data-feather=|feather[[:space:]]' "$dir" 2>/dev/null | wc -l)
    TOTAL_FEATHER=$((TOTAL_FEATHER + FEATHER_COUNT))
    echo "  🪶 Feather Icons: $FEATHER_COUNT"

    # Heroicons
    HERO_COUNT=$(grep -RInE 'heroicon|heroicons' "$dir" 2>/dev/null | wc -l)
    TOTAL_HERO=$((TOTAL_HERO + HERO_COUNT))
    echo "  🦸 Heroicons: $HERO_COUNT"

    # Remix Icons
    REMIX_COUNT=$(grep -RInE 'ri-[a-zA-Z0-9-]+' "$dir" 2>/dev/null | wc -l)
    TOTAL_REMIX=$((TOTAL_REMIX + REMIX_COUNT))
    echo "  🔄 Remix Icons: $REMIX_COUNT"

    # Boxicons
    BOX_COUNT=$(grep -RInE 'bx[[:space:]]+bx-|bxs-|bxl-' "$dir" 2>/dev/null | wc -l)
    TOTAL_BOX=$((TOTAL_BOX + BOX_COUNT))
    echo "  📦 Boxicons: $BOX_COUNT"

    # Tabler Icons
    TABLER_COUNT=$(grep -RInE 'ti[[:space:]]+ti-|tabler-icon' "$dir" 2>/dev/null | wc -l)
    TOTAL_TABLER=$((TOTAL_TABLER + TABLER_COUNT))
    echo "  📊 Tabler Icons: $TABLER_COUNT"

    # SVG Icons
    SVG_COUNT=$(grep -RIn "<svg|</svg>|<symbol|<use " "$dir" 2>/dev/null | wc -l)
    TOTAL_SVG=$((TOTAL_SVG + SVG_COUNT))
    echo "  📁 SVG Icons: $SVG_COUNT"

    # Image Files
    IMAGE_FILES=$(find "$dir" -type f \( -iname "*.svg" -o -iname "*.png" -o -iname "*.ico" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.webp" \) 2>/dev/null | wc -l)
    TOTAL_IMAGE_FILES=$((TOTAL_IMAGE_FILES + IMAGE_FILES))
    echo "  🖼️ Image Files: $IMAGE_FILES"

    echo ""
done

echo "==============================================="
echo "📊 TOTAL SUMMARY"
echo "==============================================="
echo "  🔤 Unicode Emojis:     $TOTAL_EMOJIS"
echo "  🎨 Font Awesome:        $TOTAL_FA"
echo "  🅱️ Bootstrap Icons:     $TOTAL_BI"
echo "  📐 Material Icons:      $TOTAL_MATERIAL"
echo "  ⚡ Ionicons:            $TOTAL_ION"
echo "  🪶 Feather Icons:       $TOTAL_FEATHER"
echo "  🦸 Heroicons:           $TOTAL_HERO"
echo "  🔄 Remix Icons:         $TOTAL_REMIX"
echo "  📦 Boxicons:            $TOTAL_BOX"
echo "  📊 Tabler Icons:        $TOTAL_TABLER"
echo "  📁 SVG Icons:           $TOTAL_SVG"
echo "  🖼️ Image Files:         $TOTAL_IMAGE_FILES"
echo "==============================================="
echo ""
echo "📌 TOTAL ICONS/EMOJIS USED: $((TOTAL_EMOJIS + TOTAL_FA + TOTAL_BI + TOTAL_MATERIAL + TOTAL_ION + TOTAL_FEATHER + TOTAL_HERO + TOTAL_REMIX + TOTAL_BOX + TOTAL_TABLER + TOTAL_SVG + TOTAL_IMAGE_FILES))"
echo "==============================================="
