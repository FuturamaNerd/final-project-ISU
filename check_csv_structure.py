import csv
import os

csv_path = os.path.join('data', '20250613230000.export.csv')

print(f"Examining CSV file: {csv_path}")

with open(csv_path, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    header = next(reader)
    
    print(f"CSV has {len(header)} columns:")
    for i, col in enumerate(header):
        print(f"  Column {i}: {col}")
    
    print("\nFirst few rows:")
    for i, row in enumerate(reader):
        if i < 3:  # Show first 3 rows
            print(f"Row {i+1}: {row}")
        else:
            break 