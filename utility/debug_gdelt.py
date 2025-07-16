import requests
import csv
import urllib3
import zipfile
import io

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_gdelt_file():
    # Get the latest file URL
    GDELT_CSV_URL = "https://data.gdeltproject.org/gdeltv2/lastupdate.txt"
    resp = requests.get(GDELT_CSV_URL, verify=False)
    resp.raise_for_status()
    lines = resp.text.strip().splitlines()
    csv_url = lines[0].split(' ')[-1]
    
    print(f"Fetching: {csv_url}")
    
    # Download and decompress
    resp = requests.get(csv_url, stream=True, verify=False)
    resp.raise_for_status()
    
    zip_data = io.BytesIO(resp.content)
    with zipfile.ZipFile(zip_data) as zip_file:
        csv_filename = [f for f in zip_file.namelist() if f.endswith('.CSV')][0]
        print(f"CSV file in zip: {csv_filename}")
        
        with zip_file.open(csv_filename) as csv_file:
            content = csv_file.read()
            decoded_content = content.decode('latin-1', errors='ignore')
    
    # Parse CSV
    lines = decoded_content.splitlines()
    reader = csv.reader(lines, delimiter='\t')
    
    # Print first 3 rows, all columns
    print(f"\n=== FIRST 3 ROWS, ALL COLUMNS ===")
    for row_num, row in enumerate(reader):
        if row_num >= 3:
            break
        print(f"\nRow {row_num + 1}:")
        for i, value in enumerate(row):
            print(f"  {i:2d}: {value}")
        print(f"  ... ({len(row)} total columns)")

if __name__ == "__main__":
    debug_gdelt_file() 