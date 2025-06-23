import psycopg2
from urllib.parse import urlparse

# Parse URL
db_url = "postgresql://postgres:BDDcUKtPbTqUqciUdNTYDyFHuiCsMbaj@gondola.proxy.rlwy.net:42194/railway"
conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Query to list tables in public schema
cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
""")

print("📋 Tables:")
for row in cur.fetchall():
    print(" -", row[0])

cur.close()
conn.close()
