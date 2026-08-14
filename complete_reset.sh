#!/bin/bash
pkill -f "python manage.py runserver" 2>/dev/null
deactivate 2>/dev/null
source venv/bin/activate

echo "Fixing template encoding..."
for file in templates/*.html templates/includes/*.html; do
    if [ -f "$file" ]; then
        iconv -f ISO-8859-1 -t UTF-8 "$file" 2>/dev/null > "$file.tmp" && mv "$file.tmp" "$file"
        iconv -f WINDOWS-1252 -t UTF-8 "$file" 2>/dev/null > "$file.tmp" && mv "$file.tmp" "$file"
        sed -i 's/\xEF\xBB\xBF//g' "$file" 2>/dev/null
    fi
done

find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

python manage.py flush --no-input 2>/dev/null
python manage.py makemigrations
python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

python manage.py check
echo "✅ Complete! Login: admin / admin123"
