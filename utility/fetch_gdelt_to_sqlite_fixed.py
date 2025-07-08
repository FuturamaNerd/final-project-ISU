import requests
import csv
import sqlite3
import time
import os
import json
import urllib3
import zipfile
import io
from datetime import datetime

# Disable SSL warnings and verification for GDELT
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
GDELT_CSV_URL = "https://data.gdeltproject.org/gdeltv2/lastupdate.txt"  # Use the main event file, not translation
DB_PATH = "gdelt_events.db"
COUNTRY_TO_CONTINENT_PATH = os.path.join(os.path.dirname(__file__), "countryToContinent.json")

# --- LOAD COUNTRY TO CONTINENT MAPPING ---
with open(COUNTRY_TO_CONTINENT_PATH, "r", encoding="utf-8") as f:
    COUNTRY_TO_CONTINENT = json.load(f)

def map_country_to_continent(country_code):
    return COUNTRY_TO_CONTINENT.get(country_code, "Unknown")

# --- SETUP SQLITE ---
def setup_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS gdelt_events (
            event_id TEXT PRIMARY KEY,
            date TEXT,
            event_code TEXT,
            goldstein REAL,
            actor1_name TEXT,
            actor1_country TEXT,
            actor2_name TEXT,
            actor2_country TEXT,
            latitude REAL,
            longitude REAL,
            location_name TEXT,
            continent TEXT,
            source_url TEXT
        )
    ''')
    conn.commit()
    return conn

# --- FETCH LATEST GDELT FILE URL ---
def get_latest_gdelt_csv_url():
    resp = requests.get(GDELT_CSV_URL, verify=False)
    resp.raise_for_status()
    lines = resp.text.strip().splitlines()
    latest_csv_url = lines[0].split(' ')[-1]
    return latest_csv_url

# --- DOWNLOAD AND PROCESS GDELT CSV ---
def fetch_and_store_gdelt_events():
    conn = setup_db()
    c = conn.cursor()
    csv_url = get_latest_gdelt_csv_url()
    print(f"Fetching GDELT CSV: {csv_url}")
    
    # Download the compressed file
    resp = requests.get(csv_url, stream=True, verify=False)
    resp.raise_for_status()
    
    # Handle the zip file
    if csv_url.endswith('.zip'):
        print("Decompressing zip file...")
        zip_data = io.BytesIO(resp.content)
        with zipfile.ZipFile(zip_data) as zip_file:
            csv_filename = [f for f in zip_file.namelist() if f.endswith('.CSV')][0]
            with zip_file.open(csv_filename) as csv_file:
                content = csv_file.read()
                decoded_content = content.decode('latin-1', errors='ignore')
    else:
        content = resp.content
        decoded_content = content.decode('latin-1', errors='ignore')
    
    # Process the CSV content
    lines = decoded_content.splitlines()
    reader = csv.reader(lines, delimiter='\t')
    
    # GDELT files do not have headers - first row is data
    first_row = next(reader)
    print(f"Found {len(first_row)} columns in GDELT file")
    if first_row[0].isdigit() and len(first_row[0]) > 8:
        print("First row appears to be data (no headers)")
        rows_to_process = [first_row]
    else:
        print("First row appears to be headers")
        rows_to_process = []
    
    count = 0
    max_events = 120
    processed_rows = 0
    
    # Process the first row if it was data
    for row in rows_to_process:
        processed_rows += 1
        try:
            event_id = row[0] if len(row) > 0 else None
            date = row[1] if len(row) > 1 else None
            event_code = row[26] if len(row) > 26 else None
            goldstein_str = row[30] if len(row) > 30 else None
            goldstein = float(goldstein_str) if goldstein_str and goldstein_str.strip() else None
            actor1_name = row[6] if len(row) > 6 else None
            actor1_country = row[5] if len(row) > 5 else None
            actor2_name = row[16] if len(row) > 16 else None
            actor2_country = row[15] if len(row) > 15 else None
            lat_str = row[40] if len(row) > 40 else None
            lon_str = row[41] if len(row) > 41 else None
            latitude = float(lat_str) if lat_str and lat_str.strip() and lat_str.strip() != '' else None
            longitude = float(lon_str) if lon_str and lon_str.strip() and lon_str.strip() != '' else None
            location_name = row[44] if len(row) > 44 else None
            source_url = row[60] if len(row) > 60 else None
            continent = map_country_to_continent(actor1_country) if actor1_country else 'Unknown'
            # Debug output for first few rows
            if processed_rows <= 3:
                print(f"Row {processed_rows} debug:")
                print(f"  Event ID: {event_id}")
                print(f"  Date: {date}")
                print(f"  Event Code: {event_code}")
                print(f"  Actor1: {actor1_name} ({actor1_country})")
                print(f"  Coordinates: {latitude}, {longitude}")
                print(f"  Source URL: {source_url}")
                print(f"  Location: {location_name}")
            if not source_url or latitude is None or longitude is None:
                if processed_rows <= 3:
                    print(f"  SKIPPED: Missing URL or coordinates")
                continue
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                if processed_rows <= 3:
                    print(f"  SKIPPED: Invalid coordinates")
                continue
            c.execute('''
                INSERT OR REPLACE INTO gdelt_events (
                    event_id, date, event_code, goldstein, actor1_name, actor1_country, actor2_name, actor2_country,
                    latitude, longitude, location_name, continent, source_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_id, date, event_code, goldstein, actor1_name, actor1_country, actor2_name, actor2_country,
                latitude, longitude, location_name, continent, source_url
            ))
            count += 1
            if count >= max_events:
                break
        except Exception as e:
            if processed_rows < 10:
                print(f"Error in row {processed_rows}: {e}")
            continue
    # Continue with the rest of the rows
    for row in reader:
        processed_rows += 1
        try:
            event_id = row[0] if len(row) > 0 else None
            date = row[1] if len(row) > 1 else None
            event_code = row[26] if len(row) > 26 else None
            goldstein_str = row[30] if len(row) > 30 else None
            goldstein = float(goldstein_str) if goldstein_str and goldstein_str.strip() else None
            actor1_name = row[6] if len(row) > 6 else None
            actor1_country = row[5] if len(row) > 5 else None
            actor2_name = row[16] if len(row) > 16 else None
            actor2_country = row[15] if len(row) > 15 else None
            lat_str = row[40] if len(row) > 40 else None
            lon_str = row[41] if len(row) > 41 else None
            latitude = float(lat_str) if lat_str and lat_str.strip() and lat_str.strip() != '' else None
            longitude = float(lon_str) if lon_str and lon_str.strip() and lon_str.strip() != '' else None
            location_name = row[44] if len(row) > 44 else None
            source_url = row[60] if len(row) > 60 else None
            continent = map_country_to_continent(actor1_country) if actor1_country else 'Unknown'
            if processed_rows <= 3:
                print(f"Row {processed_rows} debug:")
                print(f"  Event ID: {event_id}")
                print(f"  Date: {date}")
                print(f"  Event Code: {event_code}")
                print(f"  Actor1: {actor1_name} ({actor1_country})")
                print(f"  Coordinates: {latitude}, {longitude}")
                print(f"  Source URL: {source_url}")
                print(f"  Location: {location_name}")
            if not source_url or latitude is None or longitude is None:
                if processed_rows <= 3:
                    print(f"  SKIPPED: Missing URL or coordinates")
                continue
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                if processed_rows <= 3:
                    print(f"  SKIPPED: Invalid coordinates")
                continue
            c.execute('''
                INSERT OR REPLACE INTO gdelt_events (
                    event_id, date, event_code, goldstein, actor1_name, actor1_country, actor2_name, actor2_country,
                    latitude, longitude, location_name, continent, source_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_id, date, event_code, goldstein, actor1_name, actor1_country, actor2_name, actor2_country,
                latitude, longitude, location_name, continent, source_url
            ))
            count += 1
            if count >= max_events:
                break
        except Exception as e:
            if processed_rows < 10:
                print(f"Error in row {processed_rows}: {e}")
            continue
    conn.commit()
    conn.close()
    print(f"Processed {processed_rows} total rows")
    print(f"Stored {count} valid GDELT events in SQLite.")

if __name__ == "__main__":
    fetch_and_store_gdelt_events()
    print("Waiting 6 seconds before next allowed request...")
    time.sleep(6) 