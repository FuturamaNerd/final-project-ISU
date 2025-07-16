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
GDELT_CSV_URL = "https://data.gdeltproject.org/gdeltv2/lastupdate-translation.txt"  # This gives the latest GDELT file URLs
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
    # The second column of the first line is the latest export file
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
            # Get the first CSV file in the zip
            csv_filename = [f for f in zip_file.namelist() if f.endswith('.CSV')][0]
            with zip_file.open(csv_filename) as csv_file:
                # Try different encodings
                content = csv_file.read()
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        decoded_content = content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print("Warning: Could not decode file, using latin-1")
                    decoded_content = content.decode('latin-1', errors='ignore')
    else:
        # Handle direct CSV file
        content = resp.content
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                decoded_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            print("Warning: Could not decode file, using latin-1")
            decoded_content = content.decode('latin-1', errors='ignore')
    
    # Process the CSV content
    lines = decoded_content.splitlines()
    reader = csv.reader(lines, delimiter='\t')
    
            try:
            header = next(reader)
            print(f"Found {len(header)} columns in GDELT file")
            
            # GDELT v2 export format uses fixed column positions
            # Based on the GDELT v2 export format documentation
            field_positions = {
                'GLOBALEVENTID': 0,    # Global event ID
                'SQLDATE': 1,          # Date
                'MonthYear': 2,        # Month/Year
                'Year': 3,             # Year
                'FractionDate': 4,     # Fractional date
                'Actor1CountryCode': 5, # Actor1 country
                'Actor1Name': 6,       # Actor1 name
                'Actor1Type1Code': 7,  # Actor1 type
                'Actor1Type2Code': 8,  # Actor1 type 2
                'Actor1Type3Code': 9,  # Actor1 type 3
                'Actor2CountryCode': 15, # Actor2 country
                'Actor2Name': 16,      # Actor2 name
                'Actor2Type1Code': 17, # Actor2 type
                'Actor2Type2Code': 18, # Actor2 type 2
                'Actor2Type3Code': 19, # Actor2 type 3
                'EventCode': 26,       # Event code
                'EventBaseCode': 27,   # Event base code
                'EventRootCode': 28,   # Event root code
                'QuadClass': 29,       # Quad class
                'GoldsteinScale': 30,  # Goldstein scale
                'NumMentions': 31,     # Number of mentions
                'NumSources': 32,      # Number of sources
                'NumArticles': 33,     # Number of articles
                'AvgTone': 34,         # Average tone
                'ActionGeo_Type': 51,  # Action geo type
                'ActionGeo_FullName': 52, # Action geo full name
                'ActionGeo_CountryCode': 53, # Action geo country
                'ActionGeo_ADM1Code': 54,   # Action geo admin code
                'ActionGeo_Lat': 55,   # Action geo latitude
                'ActionGeo_Long': 56,  # Action geo longitude
                'ActionGeo_FeatureID': 57,  # Action geo feature ID
                'SOURCEURL': 58        # Source URL
            }
            
            print("Using GDELT v2 export format with fixed column positions")
        
        count = 0
        max_events = 120
        processed_rows = 0
        
        for row in reader:
            processed_rows += 1
            if processed_rows % 1000 == 0:
                print(f"Processed {processed_rows} rows, found {count} valid events...")
            
            try:
                # Safely get field values using fixed positions
                event_id = row[field_positions['GLOBALEVENTID']] if len(row) > field_positions['GLOBALEVENTID'] else None
                date = row[field_positions['SQLDATE']] if len(row) > field_positions['SQLDATE'] else None
                event_code = row[field_positions['EventCode']] if len(row) > field_positions['EventCode'] else None
                
                # Handle numeric fields
                goldstein_str = row[field_positions['GoldsteinScale']] if len(row) > field_positions['GoldsteinScale'] else None
                goldstein = float(goldstein_str) if goldstein_str and goldstein_str.strip() else None
                
                actor1_name = row[field_positions['Actor1Name']] if len(row) > field_positions['Actor1Name'] else None
                actor1_country = row[field_positions['Actor1CountryCode']] if len(row) > field_positions['Actor1CountryCode'] else None
                actor2_name = row[field_positions['Actor2Name']] if len(row) > field_positions['Actor2Name'] else None
                actor2_country = row[field_positions['Actor2CountryCode']] if len(row) > field_positions['Actor2CountryCode'] else None
                
                # Handle coordinate fields
                lat_str = row[field_positions['ActionGeo_Lat']] if len(row) > field_positions['ActionGeo_Lat'] else None
                lon_str = row[field_positions['ActionGeo_Long']] if len(row) > field_positions['ActionGeo_Long'] else None
                
                latitude = float(lat_str) if lat_str and lat_str.strip() and lat_str.strip() != '' else None
                longitude = float(lon_str) if lon_str and lon_str.strip() and lon_str.strip() != '' else None
                
                location_name = row[field_positions['ActionGeo_FullName']] if len(row) > field_positions['ActionGeo_FullName'] else None
                source_url = row[field_positions['SOURCEURL']] if len(row) > field_positions['SOURCEURL'] else None
                
                # Skip if missing essential data
                if not event_id or not date or not event_code:
                    continue
                
                continent = map_country_to_continent(actor1_country) if actor1_country else 'Unknown'
                
                # Only keep events with a URL and valid coordinates
                if not source_url or latitude is None or longitude is None:
                    continue
                
                # Validate coordinates
                if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
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
                if processed_rows < 10:  # Only show first few errors
                    print(f"Error in row {processed_rows}: {e}")
                continue
                
        conn.commit()
        conn.close()
        print(f"Processed {processed_rows} total rows")
        print(f"Stored {count} valid GDELT events in SQLite.")
        
    except Exception as e:
        print(f"Error processing CSV: {e}")
        conn.close()

if __name__ == "__main__":
    fetch_and_store_gdelt_events()
    print("Waiting 6 seconds before next allowed request...")
    time.sleep(6) 