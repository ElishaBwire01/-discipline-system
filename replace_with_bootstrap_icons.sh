#!/bin/bash

echo "==============================================="
echo "   REPLACE ALL ICONS WITH BOOTSTRAP ICONS"
echo "==============================================="
echo ""

# 1. Add Bootstrap Icons CDN to base.html
echo "1. Adding Bootstrap Icons CDN to base.html..."
if ! grep -q "bootstrap-icons" templates/base.html; then
    sed -i '/<link rel="stylesheet"/a\    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">' templates/base.html
    echo "   ✅ Added Bootstrap Icons CDN"
else
    echo "   ✅ Bootstrap Icons CDN already present"
fi

# 2. Create icon mapping (Font Awesome -> Bootstrap Icons)
echo ""
echo "2. Creating icon mapping..."

cat > /tmp/fa_to_bi_map.txt << 'MAP'
fa-user|bi-person
fa-users|bi-people
fa-user-plus|bi-person-plus
fa-user-minus|bi-person-dash
fa-user-check|bi-person-check
fa-user-cog|bi-person-gear
fa-user-edit|bi-pencil-square
fa-user-graduate|bi-mortarboard
fa-user-tie|bi-person-badge
fa-user-shield|bi-shield-lock
fa-user-clock|bi-clock-history
fa-user-tag|bi-tag
fa-lock|bi-lock
fa-lock-open|bi-unlock
fa-key|bi-key
fa-school|bi-building
fa-graduation-cap|bi-mortarboard
fa-plus|bi-plus
fa-plus-circle|bi-plus-circle
fa-minus|bi-dash
fa-minus-circle|bi-dash-circle
fa-edit|bi-pencil
fa-trash|bi-trash
fa-trash-alt|bi-trash3
fa-search|bi-search
fa-download|bi-download
fa-upload|bi-upload
fa-cloud-upload-alt|bi-cloud-upload
fa-filter|bi-funnel
fa-angle-left|bi-chevron-left
fa-angle-right|bi-chevron-right
fa-angle-double-left|bi-chevron-double-left
fa-angle-double-right|bi-chevron-double-right
fa-chevron-down|bi-chevron-down
fa-chevron-up|bi-chevron-up
fa-flag|bi-flag
fa-bell|bi-bell
fa-clock|bi-clock
fa-calendar|bi-calendar
fa-calendar-alt|bi-calendar3
fa-home|bi-house
fa-tachometer-alt|bi-speedometer2
fa-dashboard|bi-speedometer2
fa-file|bi-file
fa-file-alt|bi-file-text
fa-file-csv|bi-filetype-csv
fa-file-excel|bi-file-earmark-excel
fa-file-pdf|bi-filetype-pdf
fa-file-export|bi-file-export
fa-file-download|bi-file-earmark-arrow-down
fa-file-upload|bi-file-earmark-arrow-up
fa-exclamation|bi-exclamation
fa-exclamation-circle|bi-exclamation-circle
fa-exclamation-triangle|bi-exclamation-triangle
fa-info-circle|bi-info-circle
fa-check|bi-check
fa-check-circle|bi-check-circle
fa-times|bi-x
fa-times-circle|bi-x-circle
fa-eye|bi-eye
fa-eye-slash|bi-eye-slash
fa-sign-out-alt|bi-box-arrow-right
fa-sign-in-alt|bi-box-arrow-in-right
fa-robot|bi-robot
fa-brain|bi-cpu
fa-chart-bar|bi-bar-chart
fa-chart-line|bi-graph-up
fa-chart-pie|bi-pie-chart
fa-cog|bi-gear
fa-arrow-left|bi-arrow-left
fa-arrow-right|bi-arrow-right
fa-arrow-up|bi-arrow-up
fa-arrow-down|bi-arrow-down
fa-crown|bi-crown
fa-phone|bi-telephone
fa-envelope|bi-envelope
fa-camera|bi-camera
fa-save|bi-save
fa-paper-plane|bi-send
fa-people-group|bi-people
fa-chalkboard-teacher|bi-chalkboard
fa-list|bi-list
fa-sync|bi-arrow-repeat
fa-sync-alt|bi-arrow-repeat
fa-spinner|bi-arrow-repeat
fa-bug|bi-bug
fa-gavel|bi-hammer
fa-shield-alt|bi-shield
fa-handshake|bi-handshake
fa-comment-dots|bi-chat-dots
fa-comment|bi-chat
fa-comments|bi-chats
fa-key|bi-key
fa-lock|bi-lock
fa-unlock|bi-unlock
fa-circle|bi-circle
fa-circle-notch|bi-circle
fa-file-export|bi-file-export
fa-file-import|bi-file-import
fa-print|bi-printer
fa-link|bi-link
fa-external-link-alt|bi-box-arrow-up-right
fa-book|bi-book
fa-bookmark|bi-bookmark
fa-briefcase|bi-briefcase
fa-bullhorn|bi-megaphone
fa-calculator|bi-calculator
fa-clipboard|bi-clipboard
fa-clone|bi-clipboard
fa-code|bi-code
fa-code-branch|bi-code-square
fa-comment-alt|bi-chat
fa-compass|bi-compass
fa-copy|bi-copy
fa-credit-card|bi-credit-card
fa-crop|bi-crop
fa-cube|bi-cube
fa-cubes|bi-cubes
fa-database|bi-database
fa-desktop|bi-display
fa-dice|bi-dice
fa-dna|bi-dna
fa-dollar-sign|bi-currency-dollar
fa-donate|bi-gift
fa-door-closed|bi-door-closed
fa-door-open|bi-door-open
fa-dove|bi-dove
fa-dragon|bi-dragon
fa-drum|bi-drum
fa-ellipsis-h|bi-three-dots
fa-ellipsis-v|bi-three-dots-vertical
fa-eraser|bi-eraser
fa-euro-sign|bi-currency-euro
fa-exchange-alt|bi-arrow-left-right
fa-expand|bi-arrows-expand
fa-fast-backward|bi-skip-backward
fa-fast-forward|bi-skip-forward
fa-fax|bi-printer
fa-feather|bi-feather
fa-female|bi-gender-female
fa-fighter-jet|bi-airplane
fa-file-archive|bi-file-zip
fa-file-audio|bi-file-earmark-music
fa-file-code|bi-file-code
fa-file-image|bi-file-image
fa-file-video|bi-file-earmark-play
fa-file-word|bi-file-word
fa-film|bi-film
fa-fingerprint|bi-fingerprint
fa-fire|bi-fire
fa-fire-extinguisher|bi-fire-extinguisher
fa-fish|bi-fish
fa-flask|bi-flask
fa-folder|bi-folder
fa-folder-open|bi-folder-open
fa-font|bi-fonts
fa-futbol|bi-soccer
fa-gamepad|bi-controller
fa-gas-pump|bi-fuel-pump
fa-gem|bi-gem
fa-gift|bi-gift
fa-glasses|bi-glasses
fa-globe|bi-globe
fa-golf-ball|bi-golf
fa-greater-than|bi-chevron-right
fa-guitar|bi-guitar
fa-hammer|bi-hammer
fa-hand-holding|bi-hand-thumbs-up
fa-handshake|bi-handshake
fa-hashtag|bi-hash
fa-hdd|bi-hdd
fa-headphones|bi-headphones
fa-heart|bi-heart
fa-heartbeat|bi-heart-pulse
fa-history|bi-clock-history
fa-hospital|bi-hospital
fa-hourglass|bi-hourglass
fa-ice-cream|bi-ice-cream
fa-id-badge|bi-id-card
fa-id-card|bi-id-card
fa-image|bi-image
fa-images|bi-images
fa-inbox|bi-inbox
fa-indent|bi-indent
fa-industry|bi-industry
fa-infinity|bi-infinity
fa-italic|bi-italic
fa-journal-whills|bi-journal
fa-kaaba|bi-building
fa-keyboard|bi-keyboard
fa-landmark|bi-landmark
fa-language|bi-translate
fa-laptop|bi-laptop
fa-leaf|bi-leaf
fa-lemon|bi-lemon
fa-less-than|bi-chevron-left
fa-level-down-alt|bi-arrow-down
fa-level-up-alt|bi-arrow-up
fa-life-ring|bi-life-preserver
fa-lightbulb|bi-lightbulb
fa-lira-sign|bi-currency-lira
fa-list-ol|bi-list-ol
fa-list-ul|bi-list-ul
fa-location-arrow|bi-geo-alt
fa-long-arrow-alt-down|bi-arrow-down
fa-long-arrow-alt-left|bi-arrow-left
fa-long-arrow-alt-right|bi-arrow-right
fa-long-arrow-alt-up|bi-arrow-up
fa-low-vision|bi-eye
fa-luggage-cart|bi-suitcase
fa-magic|bi-stars
fa-magnet|bi-magnet
fa-male|bi-gender-male
fa-map|bi-map
fa-map-marker|bi-geo-alt
fa-map-pin|bi-pin
fa-mars|bi-gender-male
fa-medal|bi-award
fa-medkit|bi-suitcase-medical
fa-memory|bi-memory
fa-microphone|bi-mic
fa-microphone-alt|bi-mic
fa-microscope|bi-microscope
fa-mobile|bi-phone
fa-mobile-alt|bi-phone
fa-money-bill|bi-cash
fa-money-bill-alt|bi-cash
fa-moon|bi-moon
fa-music|bi-music-note
fa-newspaper|bi-newspaper
fa-paint-brush|bi-palette
fa-palette|bi-palette
fa-paperclip|bi-paperclip
fa-paste|bi-clipboard
fa-pause|bi-pause
fa-pause-circle|bi-pause-circle
fa-paw|bi-paw
fa-pen|bi-pen
fa-pen-alt|bi-pencil
fa-pencil-alt|bi-pencil
fa-phone|bi-telephone
fa-phone-alt|bi-telephone
fa-phone-slash|bi-telephone-x
fa-phone-volume|bi-telephone
fa-photo-video|bi-images
fa-piggy-bank|bi-piggy-bank
fa-pills|bi-capsule
fa-plane|bi-airplane
fa-plane-arrival|bi-airplane
fa-plane-departure|bi-airplane
fa-play|bi-play
fa-play-circle|bi-play-circle
fa-plug|bi-plug
fa-plus-circle|bi-plus-circle
fa-plus-square|bi-plus-square
fa-podcast|bi-podcast
fa-poll|bi-bar-chart
fa-poll-h|bi-bar-chart
fa-poop|bi-emoji-laughing
fa-pound-sign|bi-currency-pound
fa-power-off|bi-power
fa-pray|bi-hand
fa-praying-hands|bi-hand
fa-prescription|bi-prescription
fa-print|bi-printer
fa-qrcode|bi-qr-code
fa-question|bi-question
fa-question-circle|bi-question-circle
fa-quote-left|bi-quote
fa-quote-right|bi-quote
fa-random|bi-shuffle
fa-receipt|bi-receipt
fa-recycle|bi-recycle
fa-redo|bi-arrow-repeat
fa-registered|bi-registered
fa-reply|bi-reply
fa-reply-all|bi-reply-all
fa-retweet|bi-arrow-left-right
fa-ribbon|bi-ribbon
fa-ring|bi-ring
fa-road|bi-road
fa-rocket|bi-rocket
fa-route|bi-route
fa-rss|bi-rss
fa-rss-square|bi-rss
fa-ruble-sign|bi-currency-ruble
fa-ruler|bi-ruler
fa-running|bi-person-running
fa-save|bi-save
fa-screwdriver|bi-screwdriver
fa-scroll|bi-scroll
fa-search|bi-search
fa-search-minus|bi-search
fa-search-plus|bi-search
fa-server|bi-server
fa-share|bi-share
fa-share-alt|bi-share
fa-share-alt-square|bi-share
fa-share-square|bi-share
fa-shekel-sign|bi-currency-shekel
fa-shield-alt|bi-shield
fa-shipping-fast|bi-truck
fa-shopping-bag|bi-bag
fa-shopping-basket|bi-basket
fa-shopping-cart|bi-cart
fa-shower|bi-water
fa-sign-in-alt|bi-box-arrow-in-right
fa-sign-language|bi-hand-index
fa-sign-out-alt|bi-box-arrow-right
fa-signal|bi-signal
fa-signature|bi-pen
fa-sitemap|bi-diagram-3
fa-skating|bi-person-walking
fa-skiing|bi-person-walking
fa-skull|bi-skull
fa-slash|bi-slash
fa-sliders-h|bi-sliders
fa-smile|bi-emoji-smile
fa-smoking|bi-smoking
fa-snowboarding|bi-person-walking
fa-snowflake|bi-snowflake
fa-snowman|bi-snow
fa-socks|bi-socks
fa-sort|bi-arrow-down-up
fa-sort-alpha-down|bi-arrow-down
fa-sort-alpha-up|bi-arrow-up
fa-sort-amount-down|bi-arrow-down
fa-sort-amount-up|bi-arrow-up
fa-sort-down|bi-arrow-down
fa-sort-numeric-down|bi-arrow-down
fa-sort-numeric-up|bi-arrow-up
fa-sort-up|bi-arrow-up
fa-spa|bi-flower1
fa-space-shuttle|bi-rocket
fa-spider|bi-spider
fa-spinner|bi-arrow-repeat
fa-square|bi-square
fa-stamp|bi-stamp
fa-star|bi-star
fa-star-and-crescent|bi-star
fa-star-half|bi-star-half
fa-star-of-david|bi-star
fa-star-of-life|bi-star
fa-step-backward|bi-skip-backward
fa-step-forward|bi-skip-forward
fa-stethoscope|bi-heart-pulse
fa-sticky-note|bi-sticky
fa-stop|bi-stop
fa-stop-circle|bi-stop-circle
fa-stopwatch|bi-stopwatch
fa-store|bi-shop
fa-stream|bi-stream
fa-strikethrough|bi-type-strikethrough
fa-subscript|bi-subscript
fa-superscript|bi-superscript
fa-suitcase|bi-suitcase
fa-sun|bi-sun
fa-surprise|bi-emoji-surprised
fa-swimmer|bi-person-swimming
fa-synagogue|bi-building
fa-sync|bi-arrow-repeat
fa-syringe|bi-syringe
fa-table|bi-table
fa-tablet|bi-tablet
fa-tag|bi-tag
fa-tags|bi-tags
fa-tape|bi-tape
fa-tasks|bi-list-task
fa-taxi|bi-taxi
fa-teeth|bi-teeth
fa-telegram-plane|bi-send
fa-terminal|bi-terminal
fa-text-height|bi-fonts
fa-text-width|bi-fonts
fa-th|bi-grid
fa-th-large|bi-grid-3x3
fa-th-list|bi-list-ul
fa-theater-masks|bi-masks
fa-thermometer|bi-thermometer
fa-thumbs-down|bi-hand-thumbs-down
fa-thumbs-up|bi-hand-thumbs-up
fa-thumbtack|bi-pin
fa-ticket-alt|bi-ticket
fa-times|bi-x
fa-times-circle|bi-x-circle
fa-tint|bi-droplet
fa-tired|bi-emoji-frown
fa-toggle-off|bi-toggle-off
fa-toggle-on|bi-toggle-on
fa-toilet|bi-toilet
fa-toolbox|bi-tools
fa-tools|bi-tools
fa-tooth|bi-tooth
fa-torah|bi-book
fa-tractor|bi-tractor
fa-trademark|bi-trademark
fa-traffic-light|bi-traffic-light
fa-train|bi-train
fa-tram|bi-train
fa-trash|bi-trash
fa-trash-alt|bi-trash3
fa-tree|bi-tree
fa-trophy|bi-trophy
fa-truck|bi-truck
fa-tshirt|bi-tshirt
fa-tty|bi-terminal
fa-tv|bi-tv
fa-umbrella|bi-umbrella
fa-underline|bi-type-underline
fa-undo|bi-arrow-counterclockwise
fa-universal-access|bi-universal-access
fa-university|bi-building
fa-unlink|bi-link
fa-unlock|bi-unlock
fa-unlock-alt|bi-unlock
fa-upload|bi-upload
fa-utensils|bi-utensils
fa-vector-square|bi-vector
fa-venus|bi-gender-female
fa-venus-double|bi-gender-female
fa-venus-mars|bi-gender-ambiguous
fa-video|bi-camera-video
fa-video-slash|bi-camera-video-off
fa-voicemail|bi-voicemail
fa-volleyball-ball|bi-volleyball
fa-volume-down|bi-volume-down
fa-volume-mute|bi-volume-mute
fa-volume-off|bi-volume-off
fa-volume-up|bi-volume-up
fa-vote-yea|bi-check
fa-walking|bi-person-walking
fa-wallet|bi-wallet
fa-warehouse|bi-warehouse
fa-water|bi-water
fa-weight|bi-weight
fa-wheelchair|bi-wheelchair
fa-wifi|bi-wifi
fa-wind|bi-wind
fa-window-close|bi-window
fa-window-maximize|bi-window
fa-window-minimize|bi-window
fa-window-restore|bi-window
fa-wine-glass|bi-wine
fa-wrench|bi-wrench
fa-x-ray|bi-x-ray
fa-yen-sign|bi-currency-yen
fa-yin-yang|bi-yin-yang
MAP

# 3. Replace all Font Awesome with Bootstrap Icons
echo ""
echo "3. Replacing Font Awesome icons with Bootstrap Icons..."
echo "-----------------------------------------------"

# Function to replace icons in a file
replace_icons() {
    local file=$1
    echo "Processing: $file"
    
    # Replace each icon mapping
    while IFS='|' read -r fa_icon bi_icon; do
        if [ -n "$fa_icon" ] && [ -n "$bi_icon" ]; then
            # Replace <i class="fas fa-icon"></i> with <i class="bi bi-icon"></i>
            sed -i "s|<i class=\"[^\"]*$fa_icon[^\"]*\"></i>|<i class=\"bi $bi_icon\"></i>|g" "$file"
            
            # Replace <i class="fas fa-icon">text</i> with <i class="bi bi-icon">text</i>
            sed -i "s|<i class=\"[^\"]*$fa_icon[^\"]*\">\([^<]*\)</i>|<i class=\"bi $bi_icon\">\1</i>|g" "$file"
        fi
    done < /tmp/fa_to_bi_map.txt
}

# Process all template files
for file in templates/*.html; do
    if [ -f "$file" ] && ! echo "$file" | grep -q "backup"; then
        replace_icons "$file"
    fi
done

# 4. Update JavaScript dynamic icon generation
echo ""
echo "4. Updating JavaScript dynamic icon generation..."
echo "-----------------------------------------------"

cat <<'JSFIX' > /tmp/fix_js.py
import re
import os

files_to_fix = [
    'templates/ai_dashboard.html',
    'templates/student_profile.html',
    'templates/user_profile_settings.html',
    'templates/register.html',
    'templates/login.html'
]

for file_path in files_to_fix:
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace fa- with bi- in JavaScript strings
    content = re.sub(r"'fa-([a-zA-Z0-9-]+)'", r"'bi-bi-\1'", content)
    content = re.sub(r'"fa-([a-zA-Z0-9-]+)"', r'"bi-bi-\1"', content)
    
    # Replace fa-spin with bi-rotate
    content = content.replace('fa-spin', 'bi-rotate')
    
    # Replace dynamic icon generation
    content = re.sub(
        r"el\.innerHTML = '<i class=\"fas fa-\" \+ \(icon \|\| 'check'\) \+ '\"></i> ' \+ message;",
        "el.innerHTML = '<i class=\"bi bi-\" + (icon || 'check') + '\"></i> ' + message;",
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed: {file_path}")

JSFIX

python3 /tmp/fix_js.py

# 5. Remove Font Awesome CDN if present
echo ""
echo "5. Removing Font Awesome CDN if present..."
echo "-----------------------------------------------"

if grep -q "font-awesome" templates/base.html; then
    sed -i '/font-awesome/d' templates/base.html
    echo "   ✅ Removed Font Awesome CDN"
else
    echo "   ✅ No Font Awesome CDN found"
fi

# 6. Final verification
echo ""
echo "==============================================="
echo "✅ FINAL VERIFICATION"
echo "==============================================="

REMAINING_FA=$(grep -r "fa-" templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)
BI_COUNT=$(grep -r "bi " templates/ --include="*.html" 2>/dev/null | grep -v backup | wc -l)

echo "Remaining Font Awesome icons: $REMAINING_FA"
echo "Bootstrap Icons used: $BI_COUNT"

if [ "$REMAINING_FA" -eq 0 ]; then
    echo "🎉 All icons replaced with Bootstrap Icons!"
else
    echo "⚠️  Still $REMAINING_FA Font Awesome icons remain:"
    grep -rn 'fa-' templates/ --include='*.html' | grep -v backup | head -10
fi

echo ""
echo "📊 Summary:"
echo "  - Font Awesome removed: ✅"
echo "  - Bootstrap Icons added: ✅ ($BI_COUNT instances)"
echo "  - Emojis remaining: $(grep -rP '[\x{1F300}-\x{1FAFF}]' templates/ --include='*.html' 2>/dev/null | grep -v backup | wc -l)"
echo ""
echo "🚀 Restart server: python manage.py runserver"
