from flask import Blueprint, current_app
import csv
import json
import os

sql_bp = Blueprint('sql_integration', __name__)

def get_index_page_news():
    """Fetches the 3 most recent GDELT events from CSV for the index page."""
    csv_path = os.path.join(current_app.root_path, 'data', '20250613230000.export.csv')
    json_path = os.path.join(current_app.root_path, 'helper', 'countryToContinent.json')
    
    print(f"Looking for CSV file at: {csv_path}")
    print(f"Looking for JSON file at: {json_path}")
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return []
    
    if not os.path.exists(json_path):
        print(f"JSON file not found: {json_path}")
        return []
    
    # Load country to continent mapping
    with open(json_path, 'r') as f:
        country_mapping = json.load(f)
    
    print(f"Loaded {len(country_mapping)} country mappings")
    
    events = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            # Read as tab-separated values
            reader = csv.reader(file, delimiter='\t')
            next(reader)  # Skip header
            
            for i, row in enumerate(reader):
                if len(row) > 51:  # Make sure row has enough columns
                    country_code = row[51]  # ActionGeo_CountryCode
                    continent = country_mapping.get(country_code, None)
                    
                    if continent:
                        event = {
                            'country': country_code,
                            'continent': continent,
                            'title': f"Event between {row[27] or 'Unknown'} and {row[35] or 'Unknown'}",
                            'url': row[-1] if len(row) > 0 else '#',  # Last column should be URL
                            'goldstein': float(row[30]) if row[30] and row[30].replace('.', '').replace('-', '').isdigit() else 0,
                            'mentions': int(row[31]) if row[31] and row[31].isdigit() else 0
                        }
                        events.append(event)
                        print(f"Added event {len(events)}: {event['title']} from {country_code} ({continent})")
                        
                        if len(events) >= 3:
                            break
                    
                    if i > 100:  # Limit search to first 100 rows
                        break
    except Exception as e:
        print(f"Error reading CSV: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"Total events found: {len(events)}")
    return events

