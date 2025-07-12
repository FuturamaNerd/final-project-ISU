#!/usr/bin/env python3
"""
Enhanced GDELT fetcher with translation data support
"""

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
GDELT_CSV_URL = "https://data.gdeltproject.org/gdeltv2/lastupdate.txt"
GDELT_TRANSLATION_URL = "https://data.gdeltproject.org/gdeltv2/lastupdate-translation.txt"  # Translation data
DB_PATH = "gdelt_events.db"
COUNTRY_TO_CONTINENT_PATH = os.path.join(os.path.dirname(__file__), "countryToContinent.json")

# --- LOAD COUNTRY TO CONTINENT MAPPING ---
with open(COUNTRY_TO_CONTINENT_PATH, "r", encoding="utf-8") as f:
    COUNTRY_TO_CONTINENT = json.load(f)

def map_country_to_continent(country_code):
    return COUNTRY_TO_CONTINENT.get(country_code, "Unknown")

# --- SETUP SQLITE WITH TRANSLATION FIELDS ---
def setup_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Drop existing table to add new fields
    c.execute('DROP TABLE IF EXISTS gdelt_events')
    
    c.execute('''
        CREATE TABLE gdelt_events (
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
            source_url TEXT,
            -- Translation fields
            translated_title TEXT,
            translated_content TEXT,
            source_language TEXT,
            target_language TEXT,
            translation_confidence REAL,
            sentiment_score REAL,
            sentiment_magnitude REAL,
            num_mentions INTEGER,
            num_sources INTEGER,
            avg_tone REAL,
            -- Additional GDELT fields
            event_root_code TEXT,
            event_base_code TEXT,
            quad_class INTEGER,
            actor1_type1_code TEXT,
            actor1_type2_code TEXT,
            actor2_type1_code TEXT,
            actor2_type2_code TEXT,
            action_geo_type INTEGER,
            action_geo_country TEXT,
            action_geo_adm1 TEXT,
            action_geo_adm2 TEXT,
            action_geo_lat REAL,
            action_geo_long REAL,
            mention_sources TEXT,
            mention_doc_tone REAL,
            mention_doc_len INTEGER
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

# --- FETCH LATEST TRANSLATION FILE URL ---
def get_latest_translation_csv_url():
    try:
        resp = requests.get(GDELT_TRANSLATION_URL, verify=False)
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        latest_translation_url = lines[0].split(' ')[-1]
        return latest_translation_url
    except Exception as e:
        print(f"Warning: Could not fetch translation URL: {e}")
        return None

# --- DOWNLOAD AND PROCESS GDELT CSV ---
def fetch_and_store_gdelt_events():
    conn = setup_db()
    c = conn.cursor()
    
    # Fetch main events
    csv_url = get_latest_gdelt_csv_url()
    print(f"Fetching GDELT events: {csv_url}")
    
    # Fetch translations if available
    translation_url = get_latest_translation_csv_url()
    if translation_url:
        print(f"Fetching GDELT translations: {translation_url}")
    
    # Download and process main events
    events_data = download_and_parse_csv(csv_url, "events")
    
    # Download and process translations
    translations_data = {}
    if translation_url:
        translations_data = download_and_parse_csv(translation_url, "translations")
    
    # Merge events with translations
    merged_events = merge_events_with_translations(events_data, translations_data)
    
    # Store in database
    store_events_in_db(conn, c, merged_events)
    
    conn.close()
    print(f"Stored {len(merged_events)} GDELT events with translations in SQLite.")

def download_and_parse_csv(url, data_type):
    """Download and parse CSV data"""
    resp = requests.get(url, stream=True, verify=False)
    resp.raise_for_status()
    
    # Handle the zip file
    if url.endswith('.zip'):
        print(f"Decompressing {data_type} zip file...")
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
    
    data = {}
    count = 0
    max_records = 200 if data_type == "events" else 500  # More translations available
    
    for row in reader:
        if count >= max_records:
            break
            
        try:
            if data_type == "events":
                event_data = parse_event_row(row)
                if event_data:
                    data[event_data['event_id']] = event_data
                    count += 1
            elif data_type == "translations":
                translation_data = parse_translation_row(row)
                if translation_data:
                    data[translation_data['event_id']] = translation_data
                    count += 1
        except Exception as e:
            if count < 5:
                print(f"Error parsing {data_type} row: {e}")
            continue
    
    print(f"Parsed {count} {data_type} records")
    return data

def parse_event_row(row):
    """Parse a GDELT event row"""
    if len(row) < 60:
        return None
        
    try:
        event_id = row[0] if len(row) > 0 else None
        date = row[1] if len(row) > 1 else None
        event_code = row[26] if len(row) > 26 else None
        goldstein_str = row[30] if len(row) > 30 else None
        goldstein = float(goldstein_str) if goldstein_str and goldstein_str.strip() else None
        
        # Actor information
        actor1_name = row[6] if len(row) > 6 else None
        actor1_country = row[5] if len(row) > 5 else None
        actor2_name = row[16] if len(row) > 16 else None
        actor2_country = row[15] if len(row) > 15 else None
        
        # Geographic information
        lat_str = row[40] if len(row) > 40 else None
        lon_str = row[41] if len(row) > 41 else None
        latitude = float(lat_str) if lat_str and lat_str.strip() and lat_str.strip() != '' else None
        longitude = float(lon_str) if lon_str and lon_str.strip() and lon_str.strip() != '' else None
        location_name = row[44] if len(row) > 44 else None
        
        # Additional fields
        source_url = row[60] if len(row) > 60 else None
        event_root_code = row[27] if len(row) > 27 else None
        event_base_code = row[28] if len(row) > 28 else None
        quad_class = int(row[29]) if len(row) > 29 and row[29].isdigit() else None
        
        # Actor type codes
        actor1_type1_code = row[7] if len(row) > 7 else None
        actor1_type2_code = row[8] if len(row) > 8 else None
        actor2_type1_code = row[17] if len(row) > 17 else None
        actor2_type2_code = row[18] if len(row) > 18 else None
        
        # Action geography
        action_geo_type = int(row[39]) if len(row) > 39 and row[39].isdigit() else None
        action_geo_country = row[42] if len(row) > 42 else None
        action_geo_adm1 = row[43] if len(row) > 43 else None
        action_geo_adm2 = row[45] if len(row) > 45 else None
        action_geo_lat = float(row[40]) if len(row) > 40 and row[40].strip() else None
        action_geo_long = float(row[41]) if len(row) > 41 and row[41].strip() else None
        
        # Validation
        if not source_url or latitude is None or longitude is None:
            return None
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return None
            
        return {
            'event_id': event_id,
            'date': date,
            'event_code': event_code,
            'goldstein': goldstein,
            'actor1_name': actor1_name,
            'actor1_country': actor1_country,
            'actor2_name': actor2_name,
            'actor2_country': actor2_country,
            'latitude': latitude,
            'longitude': longitude,
            'location_name': location_name,
            'continent': map_country_to_continent(actor1_country) if actor1_country else 'Unknown',
            'source_url': source_url,
            'event_root_code': event_root_code,
            'event_base_code': event_base_code,
            'quad_class': quad_class,
            'actor1_type1_code': actor1_type1_code,
            'actor1_type2_code': actor1_type2_code,
            'actor2_type1_code': actor2_type1_code,
            'actor2_type2_code': actor2_type2_code,
            'action_geo_type': action_geo_type,
            'action_geo_country': action_geo_country,
            'action_geo_adm1': action_geo_adm1,
            'action_geo_adm2': action_geo_adm2,
            'action_geo_lat': action_geo_lat,
            'action_geo_long': action_geo_long
        }
    except Exception as e:
        return None

def parse_translation_row(row):
    """Parse a GDELT translation row"""
    if len(row) < 20:
        return None
        
    try:
        event_id = row[0] if len(row) > 0 else None
        translated_title = row[1] if len(row) > 1 else None
        translated_content = row[2] if len(row) > 2 else None
        source_language = row[3] if len(row) > 3 else None
        target_language = row[4] if len(row) > 4 else None
        translation_confidence = float(row[5]) if len(row) > 5 and row[5].strip() else None
        sentiment_score = float(row[6]) if len(row) > 6 and row[6].strip() else None
        sentiment_magnitude = float(row[7]) if len(row) > 7 and row[7].strip() else None
        num_mentions = int(row[8]) if len(row) > 8 and row[8].isdigit() else None
        num_sources = int(row[9]) if len(row) > 9 and row[9].isdigit() else None
        avg_tone = float(row[10]) if len(row) > 10 and row[10].strip() else None
        
        return {
            'event_id': event_id,
            'translated_title': translated_title,
            'translated_content': translated_content,
            'source_language': source_language,
            'target_language': target_language,
            'translation_confidence': translation_confidence,
            'sentiment_score': sentiment_score,
            'sentiment_magnitude': sentiment_magnitude,
            'num_mentions': num_mentions,
            'num_sources': num_sources,
            'avg_tone': avg_tone
        }
    except Exception as e:
        return None

def merge_events_with_translations(events_data, translations_data):
    """Merge events with their translations"""
    merged_events = []
    
    for event_id, event_data in events_data.items():
        translation_data = translations_data.get(event_id, {})
        
        # Merge the data
        merged_event = {**event_data, **translation_data}
        merged_events.append(merged_event)
    
    return merged_events

def store_events_in_db(conn, cursor, events):
    """Store merged events in database"""
    count = 0
    
    for event in events:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO gdelt_events (
                    event_id, date, event_code, goldstein, actor1_name, actor1_country, 
                    actor2_name, actor2_country, latitude, longitude, location_name, 
                    continent, source_url, translated_title, translated_content, 
                    source_language, target_language, translation_confidence, 
                    sentiment_score, sentiment_magnitude, num_mentions, num_sources, 
                    avg_tone, event_root_code, event_base_code, quad_class, 
                    actor1_type1_code, actor1_type2_code, actor2_type1_code, 
                    actor2_type2_code, action_geo_type, action_geo_country, 
                    action_geo_adm1, action_geo_adm2, action_geo_lat, action_geo_long
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('event_id'), event.get('date'), event.get('event_code'),
                event.get('goldstein'), event.get('actor1_name'), event.get('actor1_country'),
                event.get('actor2_name'), event.get('actor2_country'), event.get('latitude'),
                event.get('longitude'), event.get('location_name'), event.get('continent'),
                event.get('source_url'), event.get('translated_title'), event.get('translated_content'),
                event.get('source_language'), event.get('target_language'), event.get('translation_confidence'),
                event.get('sentiment_score'), event.get('sentiment_magnitude'), event.get('num_mentions'),
                event.get('num_sources'), event.get('avg_tone'), event.get('event_root_code'),
                event.get('event_base_code'), event.get('quad_class'), event.get('actor1_type1_code'),
                event.get('actor1_type2_code'), event.get('actor2_type1_code'), event.get('actor2_type2_code'),
                event.get('action_geo_type'), event.get('action_geo_country'), event.get('action_geo_adm1'),
                event.get('action_geo_adm2'), event.get('action_geo_lat'), event.get('action_geo_long')
            ))
            count += 1
        except Exception as e:
            print(f"Error storing event {event.get('event_id')}: {e}")
            continue
    
    conn.commit()
    print(f"Successfully stored {count} events in database")

if __name__ == "__main__":
    fetch_and_store_gdelt_events()
    print("Waiting 6 seconds before next allowed request...")
    time.sleep(6) 