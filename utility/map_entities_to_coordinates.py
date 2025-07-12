
import json
import pandas as pd
from pymongo import MongoClient

# Load world cities
worldcities_df = pd.read_csv('../data/worldcities.csv')
world_city_coords = {str(row['city']).strip().lower(): [float(row['lat']), float(row['lng'])] for _, row in worldcities_df.iterrows()}

# Load US cities
uscities_df = pd.read_csv('../data/uscities.csv')
us_city_coords = {(str(row['city']).strip().lower(), str(row['state_name']).strip().lower()): [float(row['lat']), float(row['lng'])] for _, row in uscities_df.iterrows()}

# Load Canada cities
canadacities_df = pd.read_csv('../data/canadacities.csv')
canada_city_coords = {(str(row['city']).strip().lower(), str(row['province_name']).strip().lower()): [float(row['lat']), float(row['lng'])] for _, row in canadacities_df.iterrows()}

# Load US counties
uscounties_df = pd.read_csv('../data/uscounties.csv')
us_county_coords = {(str(row['county']).strip().lower(), str(row['state_name']).strip().lower()): [float(row['lat']), float(row['lng'])] for _, row in uscounties_df.iterrows()}

# Load countries
countries_df = pd.read_csv('../data/countries.csv')
country_name_coords = {str(row['name']).strip().lower(): [float(row['latitude']), float(row['longitude'])] for _, row in countries_df.iterrows()}
country_code_coords = {str(row['country']).strip().upper(): [float(row['latitude']), float(row['longitude'])] for _, row in countries_df.iterrows()}

def get_coordinates_from_entities(entities):
    for name, label in entities:
        if label not in ("GPE", "LOC", "FAC"):
            continue
        key = name.strip().lower()
        # 1. World city
        coords = world_city_coords.get(key)
        if coords:
            return coords, 'world_city', name
        # 2. US city (try to extract state from context if available)
        for (city, state), coords in us_city_coords.items():
            if city == key:
                return coords, 'us_city', name
        # 3. Canada city (try to extract province from context if available)
        for (city, province), coords in canada_city_coords.items():
            if city == key:
                return coords, 'canada_city', name
        # 4. US county
        for (county, state), coords in us_county_coords.items():
            if county == key:
                return coords, 'us_county', name
        # 5. Country by name
        coords = country_name_coords.get(key)
        if coords:
            return coords, 'country', name
        # 6. Country by code (if entity is a code)
        code = name.strip().upper()
        coords = country_code_coords.get(code)
        if coords:
            return coords, 'country_code', name
    return None, None, None

def update_newsapi_with_coordinates():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["news_world_database"]
    collection = db["news_by_location"]

    updated = 0
    for doc in collection.find():
        entities = doc.get('entities', [])
        coords, precision, location_name = get_coordinates_from_entities(entities)
        if coords:
            update = {
                "latitude": coords[0],
                "longitude": coords[1],
                "location_precision": precision,
                "location_name": location_name
            }
        else:
            update = {
                "latitude": None,
                "longitude": None,
                "location_precision": None,
                "location_name": None
            }
        result = collection.update_one({"_id": doc["_id"]}, {"$set": update})
        if result.modified_count > 0:
            updated += 1
    print(f"Updated {updated} documents with coordinates.")

if __name__ == "__main__":
    update_newsapi_with_coordinates() 
