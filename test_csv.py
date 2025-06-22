import csv
import json
import os

# Test CSV reading
csv_path = os.path.join('data', '20250613230000.export.csv')
json_path = os.path.join('helper', 'countryToContinent.json')

print(f"Testing CSV file: {csv_path}")
print(f"Testing JSON file: {json_path}")

# Check if files exist
if os.path.exists(csv_path):
    print("✓ CSV file found")
else:
    print("✗ CSV file not found")
    exit()

if os.path.exists(json_path):
    print("✓ JSON file found")
else:
    print("✗ JSON file not found")
    exit()

# Load JSON mapping
with open(json_path, 'r') as f:
    country_mapping = json.load(f)
print(f"Loaded {len(country_mapping)} country mappings")

# Read first few rows of CSV
with open(csv_path, 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='\t')  # Use tab delimiter
    header = next(reader)
    print(f"CSV has {len(header)} columns")
    
    events_found = 0
    for i, row in enumerate(reader):
        if len(row) > 51:
            country_code = row[51]
            continent = country_mapping.get(country_code, None)
            
            if continent:
                events_found += 1
                print(f"Event {events_found}: {country_code} -> {continent}")
                print(f"  Actor1: {row[27]}")
                print(f"  Actor2: {row[35]}")
                print(f"  URL: {row[-1] if len(row) > 0 else 'N/A'}")
                
                if events_found >= 3:
                    break
        
        if i > 50:  # Limit to first 50 rows
            break

print(f"Total events found: {events_found}") 