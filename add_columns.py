import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.conf import settings

db_path = settings.DATABASES['default']['NAME']

# Connect to SQLite
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check if custom_case column exists
cursor.execute("PRAGMA table_info(core_disciplinereport)")
columns = [col[1] for col in cursor.fetchall()]

added = False

# Add custom_case column if missing
if 'custom_case' not in columns:
    try:
        cursor.execute("ALTER TABLE core_disciplinereport ADD COLUMN custom_case varchar(200) NULL")
        print("✅ Added custom_case column")
        added = True
    except Exception as e:
        print(f"❌ Failed to add custom_case: {e}")

# Add rating column if missing
if 'rating' not in columns:
    try:
        cursor.execute("ALTER TABLE core_disciplinereport ADD COLUMN rating integer DEFAULT 1")
        print("✅ Added rating column")
        added = True
    except Exception as e:
        print(f"❌ Failed to add rating: {e}")

if not added:
    print("ℹ️ Columns already exist")

conn.commit()
conn.close()
