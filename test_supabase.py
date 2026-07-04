import psycopg2
import os

print("?? Testing Supabase connection...")

try:
    conn = psycopg2.connect(
        host="aws-1-eu-north-1.pooler.supabase.com",
        user="postgres.murnebrvgejmxdxzxtfe",
        password="bwire10.20.",
        dbname="postgres",
        port="5432",
        sslmode="require",
        connect_timeout=15
    )
    print("? Supabase PostgreSQL connection successful!")
    
    with conn.cursor() as cur:
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"?? PostgreSQL Version: {version[0][:50]}...")
    
    conn.close()
    print("")
    print("?? Connection Details:")
    print(f"   Host: aws-1-eu-north-1.pooler.supabase.com")
    print(f"   Port: 5432")
    print(f"   Database: postgres")
    print(f"   User: postgres.murnebrvgejmxdxzxtfe")
    print(f"   Mode: Session Pooler (IPv4)")
    
except Exception as e:
    print(f"? Connection failed: {e}")
    print("")
    print("?? Troubleshooting:")
    print("   1. Make sure you're connected to the internet")
    print("   2. Check if Supabase project is running")
    print("   3. Verify the password is correct")
    print("   4. Try using Transaction Pooler with port 6543")