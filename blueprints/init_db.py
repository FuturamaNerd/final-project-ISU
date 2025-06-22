import sqlite3
import csv
import os
import json
from flask import Blueprint, current_app

gdelt_bp = Blueprint('gdelt', __name__)

@gdelt_bp.route('/load-gdelt')
def load_gdelt_data():
    # Dynamically construct path to CSV
    csv_path = os.path.join(current_app.root_path, 'data', '20250613230000.export.csv')

    conn = sqlite3.connect(os.path.join(current_app.root_path, 'data', 'news.db'))
    cursor = conn.cursor()

    # Create table 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gdelt_events (
            GLOBALEVENTID INTEGER PRIMARY KEY,
            SQLDATE TEXT,
            MonthYear INTEGER,
            Year INTEGER,
            Actor1Name TEXT,
            Actor2Name TEXT,
            ActionGeo_CountryCode TEXT,
            GoldsteinScale REAL,
            NumMentions INTEGER
        )
    ''')

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip header

        for row in reader:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO gdelt_events (
                        GLOBALEVENTID, SQLDATE, MonthYear, Year,
                        Actor1Name, Actor2Name, ActionGeo_CountryCode,
                        GoldsteinScale, NumMentions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    int(row[0]),
                    row[1],
                    int(row[2]),
                    int(row[3]),
                    row[27],
                    row[35],
                    row[51],
                    float(row[30]),
                    int(row[31])
                ))
            except Exception as e:
                print(f"Skipping row due to error: {e}")

    # Load country code to continent mapping from JSON file
    json_path = os.path.join(current_app.root_path, 'helper', 'countryToContinent.json')
    with open(json_path, 'r') as f:
        countryToContinent = json.load(f)

    # Add continent column to the table
    cursor.execute('''
        ALTER TABLE gdelt_events ADD COLUMN continent TEXT
    ''')

    # Update the continent column based on the country code
    for country_code, continent in countryToContinent.items():
        cursor.execute('''
            UPDATE gdelt_events
            SET continent = ?
            WHERE ActionGeo_CountryCode = ?
        ''', (continent, country_code))


    conn.commit()
    conn.close()
 
    return "created database!"