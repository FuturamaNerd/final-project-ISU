import sqlite3
import os

# --- Configuration ---
DB_FILE = os.path.join('data', 'news.db')
TABLE_TO_CHECK = 'news'
# ---------------------

if not os.path.exists(DB_FILE):
    print(f"Error: Database file not found at '{DB_FILE}'")
    exit()

print(f"Connecting to {DB_FILE}...")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

try:
    print(f"--- Checking contents of '{TABLE_TO_CHECK}' table ---")
    cursor.execute(f"SELECT * FROM {TABLE_TO_CHECK} LIMIT 10") # Limit to 10 rows for a quick check
    rows = cursor.fetchall()
    
    if not rows:
        print(f"The '{TABLE_TO_CHECK}' table is empty or does not exist.")
    else:
        # Get column names
        column_names = [description[0] for description in cursor.description]
        print("Column Names:", column_names)
        print("-" * 20)
        
        print(f"Found {len(rows)} row(s). Showing up to 10:")
        for row in rows:
            print(row)

except sqlite3.OperationalError as e:
    print(f"An error occurred: {e}")
    print(f"This might mean the table '{TABLE_TO_CHECK}' doesn't exist.")

finally:
    conn.close()
    print("\nConnection closed.") 