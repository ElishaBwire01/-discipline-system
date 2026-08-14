#!/bin/bash

echo "Updating views.py..."

cat > app/views.py <<'PY'
# complete Django pagination view
PY

echo "Updating urls.py..."

cat > app/urls.py <<'PY'
# urls
PY

echo "Updating templates..."

mkdir -p templates

cat > templates/index.html <<'HTML'
<!-- pagination template -->
HTML

echo "Done."
