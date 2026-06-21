import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
django.setup()

from django.db import connection

# Check if table exists
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_passwordreset'")
    result = cursor.fetchone()
    
    if result:
        print("✓ PasswordReset table exists!")
        print(f"  Table name: {result[0]}")
    else:
        print("✗ PasswordReset table does NOT exist!")
        print("  Creating manually...")
        
        # Create table manually
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS core_passwordreset (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                requested_at DATETIME NOT NULL,
                resolved_at DATETIME,
                resolved_by_id INTEGER,
                status VARCHAR(20) NOT NULL,
                new_password VARCHAR(128),
                notes TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES auth_user (id),
                FOREIGN KEY (resolved_by_id) REFERENCES auth_user (id)
            )
        ''')
        print("✓ PasswordReset table created manually!")
