#!/usr/bin/env python3
"""
Debug script to inspect GDELT database contents
"""

import sqlite3
import json
from datetime import datetime

def debug_gdelt_database():
    """Debug the GDELT database to see what data is available"""
    
    try:
        # Connect to the database
        conn = sqlite3.connect('gdelt_events.db')
        cursor = conn.cursor()
        
        # Get table info
        print("=== GDELT DATABASE DEBUG ===\n")
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in database: {tables}")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(gdelt_events);")
        columns = cursor.fetchall()
        print(f"\nTable schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM gdelt_events;")
        total_count = cursor.fetchone()[0]
        print(f"\nTotal records: {total_count}")
        
        # Get sample records
        print(f"\n=== SAMPLE RECORDS ===")
        cursor.execute('''
            SELECT event_id, date, event_code, goldstein, actor1_name, actor1_country, 
                   actor2_name, actor2_country, latitude, longitude, location_name, 
                   continent, source_url FROM gdelt_events LIMIT 5
        ''')
        
        sample_records = cursor.fetchall()
        for i, record in enumerate(sample_records, 1):
            print(f"\nRecord {i}:")
            print(f"  event_id: {record[0]}")
            print(f"  date: {record[1]}")
            print(f"  event_code: {record[2]}")
            print(f"  goldstein: {record[3]}")
            print(f"  actor1_name: {record[4]}")
            print(f"  actor1_country: {record[5]}")
            print(f"  actor2_name: {record[6]}")
            print(f"  actor2_country: {record[7]}")
            print(f"  latitude: {record[8]}")
            print(f"  longitude: {record[9]}")
            print(f"  location_name: {record[10]}")
            print(f"  continent: {record[11]}")
            print(f"  source_url: {record[12]}")
        
        # Check for null/empty values
        print(f"\n=== NULL/EMPTY VALUE ANALYSIS ===")
        
        fields = ['location_name', 'date', 'event_code', 'actor1_name', 'actor2_name', 'latitude', 'longitude']
        for field in fields:
            cursor.execute(f"SELECT COUNT(*) FROM gdelt_events WHERE {field} IS NULL OR {field} = '';")
            null_count = cursor.fetchone()[0]
            percentage = (null_count / total_count * 100) if total_count > 0 else 0
            print(f"  {field}: {null_count}/{total_count} null/empty ({percentage:.1f}%)")
        
        # Check coordinate ranges
        print(f"\n=== COORDINATE ANALYSIS ===")
        cursor.execute("SELECT MIN(latitude), MAX(latitude), MIN(longitude), MAX(longitude) FROM gdelt_events WHERE latitude IS NOT NULL AND longitude IS NOT NULL;")
        coords = cursor.fetchone()
        if coords[0] is not None:
            print(f"  Latitude range: {coords[0]} to {coords[1]}")
            print(f"  Longitude range: {coords[2]} to {coords[3]}")
        else:
            print("  No valid coordinates found")
        
        # Check date format
        print(f"\n=== DATE ANALYSIS ===")
        cursor.execute("SELECT DISTINCT date FROM gdelt_events WHERE date IS NOT NULL AND date != '' LIMIT 5;")
        dates = cursor.fetchall()
        print(f"  Sample dates: {[d[0] for d in dates]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error debugging GDELT database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_gdelt_database() 