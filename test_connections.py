import psycopg2
import os

# Your Supabase details
host = "murnebrvgejmxdxzxtfe.supabase.co"
user = "postgres"
password = "10.20.30.40"  # Your password
dbname = "postgres"

# Test configurations
configs = [
    {"sslmode": "require", "port": 5432},
    {"sslmode": "disable", "port": 5432},
    {"sslmode": "require", "port": 6543},
    {"sslmode": "require", "port": 5432, "connect_timeout": 10},
]

print(f"Testing connection to {host}...")
print("-" * 50)

for config in configs:
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname,
            port=config.get("port", 5432),
            sslmode=config.get("sslmode", "require"),
            connect_timeout=config.get("connect_timeout", 30)
        )
        print(f"? Connected! Configuration: {config}")
        conn.close()
        break
    except Exception as e:
        print(f"? Failed with {config}: {str(e)[:100]}")

# Alternative: Try connection string
try:
    import os
    # Try with full connection string
    conn = psycopg2.connect(
        "postgresql://postgres:10.20.30.40@murnebrvgejmxdxzxtfe.supabase.co:5432/postgres?sslmode=require"
    )
    print("? Connected with connection string!")
    conn.close()
except Exception as e:
    print(f"? Connection string failed: {e}")