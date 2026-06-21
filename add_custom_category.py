import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.conf import settings

db_path = settings.DATABASES['default']['NAME']
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(core_disciplinereport)")
columns = [col[1] for col in cursor.fetchall()]

if 'custom_category' not in columns:
    cursor.execute("ALTER TABLE core_disciplinereport ADD COLUMN custom_category varchar(200) NULL")
    print("✅ Added custom_category column")
else:
    print("ℹ️ custom_category column already exists")

# Remove custom_case if exists
if 'custom_case' in columns:
    # SQLite doesn't support DROP COLUMN directly, so we just ignore it
    print("ℹ️ custom_case column exists but will be ignored")

conn.commit()
conn.close()
print("✅ Database update complete")
