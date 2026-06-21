import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.conf import settings

db_path = settings.DATABASES['default']['NAME']
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(core_disciplinereport)")
columns = [col[1] for col in cursor.fetchall()]

# Add category_name if not exists
if 'category_name' not in columns:
    cursor.execute("ALTER TABLE core_disciplinereport ADD COLUMN category_name varchar(200) NULL")
    print("✅ Added category_name column")
else:
    print("ℹ️ category_name already exists")

# Add points if not exists
if 'points' not in columns:
    cursor.execute("ALTER TABLE core_disciplinereport ADD COLUMN points integer DEFAULT 0")
    print("✅ Added points column")
else:
    print("ℹ️ points already exists")

# Remove category_id foreign key (SQLite doesn't support DROP COLUMN, so we just ignore it)
print("ℹ️ category_id column still exists but will be ignored")

conn.commit()
conn.close()
print("✅ Database update complete")
