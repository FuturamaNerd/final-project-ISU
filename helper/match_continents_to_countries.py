import sqlite3
import json
import os

# Load the country to continent mapping
with open(os.path.join(os.path.dirname(__file__), 'countryToContinent.json'), 'r') as f:
    country_to_continent = json.load(f)

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'news.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Add the continent column if it doesn't exist
try:
    cursor.execute("ALTER TABLE countries ADD COLUMN continent TEXT")
except sqlite3.OperationalError:
    print("Column already exists, skipping ALTER TABLE.")

# 2. Update the continent for each country
for country_code, continent in country_to_continent.items():
    # If your countries table uses country names, you may need to map codes to names
    cursor.execute("UPDATE countries SET continent = ? WHERE name = ?", (continent, country_code))

conn.commit()
conn.close()
print("Continent column added and updated.")