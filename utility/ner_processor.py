"""
Named Entity Recognition (NER) processor using spaCy for news articles.
Extracts location entities from article content and maps them to coordinates using CSV files.
"""

import spacy
from typing import List, Dict, Optional, Tuple
import json
import os
from pathlib import Path
from utility.news_scraper import scrape_article_text
from flask_pymongo import PyMongo
from flask import Flask
from pymongo import MongoClient
import re
import pandas as pd

def extract_dateline(text):
    # Try the flexible city, country pattern first
    match = re.match(r'^[\"\']?([A-Za-z\s\.\'-]+,\s*[A-Za-z\s\.\'-]+)\s*--', text.strip(), re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: single all-caps word at the start (e.g., "WASHINGTON")
    match2 = re.match(r'^([A-Z][A-Z\s]+)\b', text.strip())
    if match2:
        candidate = match2.group(1).strip()
        # Optionally, filter out very short words or common non-location words
        if len(candidate) > 3:  # Avoid matching "THE", "AND", etc.
            return candidate.title()  # Return as title case for consistency
    return None

# Test line for extract_dateline
print('Test dateline extraction:', extract_dateline('WASHINGTON The Supreme Court on Thursday waded into the legal fight ov…'))

# Load spaCy model (will download if not available)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("⚠️  spaCy English model not found. Installing...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class NERProcessor:
    """Process news articles to extract location entities using spaCy."""
    
    def __init__(self):
        """Initialize the NER processor."""
        self.nlp = nlp
        self.location_cache = {}
        self._load_location_data()
        print("✅ NER Processor initialized with CSV coordinate data")

    def _load_location_data(self):
        """Load location data from CSV files for coordinate mapping."""
        try:
            data_dir = Path(__file__).parent.parent / "data"
            
            # Load world cities
            worldcities_path = data_dir / "worldcities.csv"
            if worldcities_path.exists():
                worldcities_df = pd.read_csv(worldcities_path)
                self.world_city_coords = {str(row['city']).strip().lower(): [float(row['lat']), float(row['lng'])] 
                                        for _, row in worldcities_df.iterrows()}
                print(f"✅ Loaded {len(self.world_city_coords)} world cities")
            else:
                self.world_city_coords = {}
                print("⚠️  worldcities.csv not found")
            
            # Load US cities
            uscities_path = data_dir / "uscities.csv"
            if uscities_path.exists():
                uscities_df = pd.read_csv(uscities_path)
                self.us_city_coords = {(str(row['city']).strip().lower(), str(row['state_name']).strip().lower()): 
                                     [float(row['lat']), float(row['lng'])] for _, row in uscities_df.iterrows()}
                print(f"✅ Loaded {len(self.us_city_coords)} US cities")
            else:
                self.us_city_coords = {}
                print("⚠️  uscities.csv not found")
            
            # Load Canada cities
            canadacities_path = data_dir / "canadacities.csv"
            if canadacities_path.exists():
                canadacities_df = pd.read_csv(canadacities_path)
                self.canada_city_coords = {(str(row['city']).strip().lower(), str(row['province_name']).strip().lower()): 
                                         [float(row['lat']), float(row['lng'])] for _, row in canadacities_df.iterrows()}
                print(f"✅ Loaded {len(self.canada_city_coords)} Canada cities")
            else:
                self.canada_city_coords = {}
                print("⚠️  canadacities.csv not found")
            
            # Load US counties
            uscounties_path = data_dir / "uscounties.csv"
            if uscounties_path.exists():
                uscounties_df = pd.read_csv(uscounties_path)
                self.us_county_coords = {(str(row['county']).strip().lower(), str(row['state_name']).strip().lower()): 
                                       [float(row['lat']), float(row['lng'])] for _, row in uscounties_df.iterrows()}
                print(f"✅ Loaded {len(self.us_county_coords)} US counties")
            else:
                self.us_county_coords = {}
                print("⚠️  uscounties.csv not found")
            
            # Load countries
            countries_path = data_dir / "countries.csv"
            if countries_path.exists():
                countries_df = pd.read_csv(countries_path)
                self.country_name_coords = {str(row['name']).strip().lower(): [float(row['latitude']), float(row['longitude'])] 
                                          for _, row in countries_df.iterrows()}
                self.country_code_coords = {str(row['country']).strip().upper(): [float(row['latitude']), float(row['longitude'])] 
                                          for _, row in countries_df.iterrows()}
                print(f"✅ Loaded {len(self.country_name_coords)} countries")
            else:
                self.country_name_coords = {}
                self.country_code_coords = {}
                print("⚠️  countries.csv not found")
                
        except Exception as e:
            print(f"❌ Error loading location data: {e}")
            self.world_city_coords = {}
            self.us_city_coords = {}
            self.canada_city_coords = {}
            self.us_county_coords = {}
            self.country_name_coords = {}
            self.country_code_coords = {}

    def get_coordinates_from_entities(self, entities):
        """Get coordinates from a list of entities using CSV data."""
        for name, label in entities:
            if label not in ("GPE", "LOC", "FAC"):
                continue
            key = name.strip().lower()
            
            # 1. World city
            coords = self.world_city_coords.get(key)
            if coords:
                return coords, 'world_city', name
            
            # 2. US city (try to extract state from context if available)
            for (city, state), coords in self.us_city_coords.items():
                if city == key:
                    return coords, 'us_city', name
            
            # 3. Canada city (try to extract province from context if available)
            for (city, province), coords in self.canada_city_coords.items():
                if city == key:
                    return coords, 'canada_city', name
            
            # 4. US county
            for (county, state), coords in self.us_county_coords.items():
                if county == key:
                    return coords, 'us_county', name
            
            # 5. Country by name
            coords = self.country_name_coords.get(key)
            if coords:
                return coords, 'country', name
            
            # 6. Country by code (if entity is a code)
            code = name.strip().upper()
            coords = self.country_code_coords.get(code)
            if coords:
                return coords, 'country_code', name
        
        return None, None, None

    def extract_locations_with_dateline_and_title(self, article):
        locations = []
        # 1. Dateline from content
        content = article.get('content', '') or ''
        dateline = extract_dateline(content)
        if dateline:
            locations.append({
                'text': dateline,
                'label': 'DATELINE',
                'confidence': 1.0,
                'description': 'Dateline location'
            })
        # 2. Locations from title
        title = article.get('title', '') or ''
        doc_title = self.nlp(title)
        for ent in doc_title.ents:
            if ent.label_ in ['GPE', 'LOC', 'FAC']:
                locations.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'confidence': 0.8,
                    'description': 'spaCy NER (title)'
                })
        # 3. Locations from content (usual NER)
        doc_content = self.nlp(content)
        for ent in doc_content.ents:
            if ent.label_ in ['GPE', 'LOC', 'FAC']:
                locations.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'confidence': 0.8,
                    'description': 'spaCy NER (content)'
                })
        # Remove duplicates while preserving order
        seen = set()
        unique_locations = []
        for loc in locations:
            if loc['text'].lower() not in seen:
                seen.add(loc['text'].lower())
                unique_locations.append(loc)
        return unique_locations

    def _get_entity_description(self, label: str) -> str:
        """Get a human-readable description of the entity label."""
        descriptions = {
            'GPE': 'Country, City, or State',
            'LOC': 'Location or Place',
            'FAC': 'Building or Facility',
            'ORG': 'Organization',
            'PERSON': 'Person',
            'EVENT': 'Event',
            'WORK_OF_ART': 'Work of Art',
            'LAW': 'Law',
            'LANGUAGE': 'Language',
            'DATE': 'Date',
            'TIME': 'Time',
            'PERCENT': 'Percentage',
            'MONEY': 'Money',
            'QUANTITY': 'Quantity',
            'ORDINAL': 'Ordinal',
            'CARDINAL': 'Cardinal Number'
        }
        return descriptions.get(label, 'Unknown')

    def process_article(self, article: Dict) -> Dict:
        """
        Process a news article to extract location entities.
        """
        if not article:
            return article
        # Extract locations using dateline and title
        locations = self.extract_locations_with_dateline_and_title(article)
        article['extracted_locations'] = locations
        article['location_count'] = len(locations)
        return article

    def process_multiple_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Process multiple articles to extract location entities.
        """
        processed_articles = []
        for i, article in enumerate(articles):
            print(f"Processing article {i+1}/{len(articles)}: {article.get('title', 'No title')[:50]}...")
            processed_article = self.process_article(article)
            processed_articles.append(processed_article)
        return processed_articles

# Global instance for easy access
ner_processor = NERProcessor() 

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def process_and_store_articles_with_ner(articles, mongo_uri, collection_name="news_by_location"):
    """Process articles with NER and store them with location data."""
    client = MongoClient(mongo_uri)
    db = client.get_default_database()  # This will use the DB from the URI
    collection = db[collection_name]
    
    print(f"Processing {len(articles)} articles with NER...")
    
    for i, article in enumerate(articles):
        print(f"Processing article {i+1}/{len(articles)}: {article.get('title', 'No title')[:50]}...")
        
        url = article.get('url')
        country_code = article.get('country') or article.get('source_country')
        
        # Scrape full text if URL is available
        full_text = scrape_article_text(url) if url else None
        
        if full_text:
            # Extract entities from full text
            entities = extract_entities(full_text)
            
            # Get coordinates from entities using CSV data
            coords, precision, location_name = ner_processor.get_coordinates_from_entities(entities)
            
            # Update article with NER data
            article['full_text'] = full_text
            article['entities'] = entities
            article['country_code'] = country_code
            
            if coords:
                article['longitude'] = coords[1]
                article['latitude'] = coords[0]
                article['coordinates'] = coords
                article['location_precision'] = precision
                article['location_name'] = location_name
                print(f"  ✅ Found coordinates: {coords} ({precision})")
            else:
                article['longitude'] = None
                article['latitude'] = None
                article['coordinates'] = None
                article['location_precision'] = None
                article['location_name'] = None
                print(f"  ⚠️  No coordinates found")
        else:
            article['full_text'] = None
            article['entities'] = []
            article['country_code'] = country_code if country_code else None
            article['longitude'] = None
            article['latitude'] = None
            article['coordinates'] = None
            article['location_precision'] = None
            article['location_name'] = None
            print(f"  ⚠️  Could not scrape article text")
        
        # Remove the _id field if it exists to avoid conflicts
        article.pop('_id', None)
        
        # Insert or update the article
        collection.insert_one(article)
        print(f"  💾 Stored article in {collection_name}")
    
    print(f"✅ Completed processing {len(articles)} articles")
    client.close()

if __name__ == "__main__":
    # Test the NER processor
    print("Testing NER Processor...")
    test_article = {
        'title': 'Breaking news from New York City',
        'content': 'WASHINGTON -- The president made an announcement today.',
        'url': 'https://example.com'
    }
    
    processed = ner_processor.process_article(test_article)
    print(f"Extracted locations: {processed.get('extracted_locations', [])}")