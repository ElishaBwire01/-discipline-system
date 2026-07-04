import psycopg2
import os

print("?? Testing Supabase connection...")

try:
    conn = psycopg2.connect(
        host="murnebrvgejmxdxzxtfe.supabase.co",
        user="postgres",
        password="bwire10.20.",
        dbname="postgres",
        port="6543",
        sslmode="require",
        connect_timeout=10
    )
    print("? Supabase PostgreSQL connection successful!")
    print("?? Connection info:", conn.get_dsn_parameters())
    conn.close()
    
    # Test with Django settings
    print("\n?? Testing Django connection...")
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')
    django.setup()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"? PostgreSQL Version: {version[0][:50]}...")
    
except Exception as e:
    print(f"? Connection failed: {e}")
    print("\n?? Troubleshooting tips:")
    print("   1. Check if Supabase is running")
    print("   2. Verify the password is correct")
    print("   3. Try using port 5432 instead of 6543")
    print("   4. Check your network/firewall settings")