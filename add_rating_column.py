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

if 'rating' not in columns:
    cursor.execute("ALTER TABLE core_disciplinereport ADD COLUMN rating varchar(20) DEFAULT 'MODERATE'")
    print("✅ Added rating column")
else:
    print("ℹ️ Rating column already exists")

conn.commit()
conn.close()
