import sqlite3
import os

db_path = os.path.join('data', 'news.db')

if not os.path.exists(db_path):
    print(f"Database file not found: {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"Tables in {db_path}:")
for table in tables:
    print(f"  - {table[0]}")

conn.close() 