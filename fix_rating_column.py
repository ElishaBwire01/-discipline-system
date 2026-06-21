import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.conf import settings

db_path = settings.DATABASES['default']['NAME']
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check if rating column exists
cursor.execute("PRAGMA table_info(core_disciplinereport)")
columns = [col[1] for col in cursor.fetchall()]

if 'rating' not in columns:
    cursor.execute("ALTER TABLE core_disciplinereport ADD COLUMN rating varchar(20) DEFAULT 'MODERATE'")
    print("✅ Added rating column")
else:
    print("ℹ️ Rating column already exists")

# Update existing NULL ratings to MODERATE
cursor.execute("UPDATE core_disciplinereport SET rating = 'MODERATE' WHERE rating IS NULL OR rating = ''")
print("✅ Updated existing records")

conn.commit()
conn.close()
print("✅ Database update complete")
