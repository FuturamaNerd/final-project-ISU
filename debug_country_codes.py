import csv
import json
import os

csv_path = os.path.join('data', '20250613230000.export.csv')
json_path = os.path.join('helper', 'countryToContinent.json')

# Load JSON mapping
with open(json_path, 'r') as f:
    country_mapping = json.load(f)

print(f"JSON mapping has {len(country_mapping)} countries")
print("Sample JSON keys:", list(country_mapping.keys())[:10])

# Check CSV country codes
csv_country_codes = set()

with open(csv_path, 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='\t')
    next(reader)  # Skip header
    
    for i, row in enumerate(reader):
        if len(row) > 51:
            country_code = row[51]
            if country_code and country_code.strip():
                csv_country_codes.add(country_code.strip())
        
        if i > 100:  # Check first 100 rows
            break

print(f"\nCSV has {len(csv_country_codes)} unique country codes")
print("Sample CSV country codes:", list(csv_country_codes)[:10])

# Check for matches
matches = []
for code in csv_country_codes:
    if code in country_mapping:
        matches.append(code)

print(f"\nFound {len(matches)} matching country codes:")
for code in matches[:10]:
    print(f"  {code} -> {country_mapping[code]}")

# Show some non-matching codes
non_matches = [code for code in list(csv_country_codes)[:10] if code not in country_mapping]
print(f"\nSample non-matching codes: {non_matches}") 