"""
Named Entity Recognition (NER) processor using spaCy for news articles.
Extracts location entities from article content and maps them to coordinates.
"""

import spacy
from typing import List, Dict, Optional, Tuple
import json
import os
from pathlib import Path
from utility.news_scraper import scrape_article_text
from flask_pymongo import PyMongo
from flask import Flask
from fetch_news_smart import get_country_coordinates
from pymongo import MongoClient
import re

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
    
    def _load_location_data(self):
        """Load location data from the country-to-continent mapping."""
        try:
            config_path = Path(__file__).parent / "config.py"
            country_data_path = Path(__file__).parent / "countryToContinent.json"
            
            if country_data_path.exists():
                with open(country_data_path, 'r', encoding='utf-8') as f:
                    self.country_data = json.load(f)
                print(f"✅ Loaded {len(self.country_data)} country mappings")
            else:
                print("⚠️  countryToContinent.json not found, using basic location data")
                self.country_data = {}
        except Exception as e:
            print(f"❌ Error loading location data: {e}")
            self.country_data = {}
    
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
        
        Args:
            article (Dict): The news article dictionary
            
        Returns:
            Dict: Article with added location entities
        """
        if not article:
            return article
        
        # Extract text content from various fields
        text_fields = []
        if article.get('title'):
            text_fields.append(article['title'])
        if article.get('description'):
            text_fields.append(article['description'])
        if article.get('content'):
            text_fields.append(article['content'])
        
        # Combine all text for analysis
        combined_text = ' '.join(text_fields)
        
        # Extract locations
        locations = self.extract_locations_with_dateline_and_title(article)
        
        # Add location data to article
        article['extracted_locations'] = locations
        article['location_count'] = len(locations)
        
        # Get the most prominent location (first one found)
        if locations:
            article['primary_location'] = locations[0]['text']
        else:
            article['primary_location'] = None
        
        return article
    
    def process_multiple_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Process multiple articles to extract location entities.
        
        Args:
            articles (List[Dict]): List of news articles
            
        Returns:
            List[Dict]: Articles with added location entities
        """
        processed_articles = []
        
        for i, article in enumerate(articles):
            print(f"Processing article {i+1}/{len(articles)}: {article.get('title', 'No title')[:50]}...")
            processed_article = self.process_article(article)
            processed_articles.append(processed_article)
        
        return processed_articles
    
    def get_location_statistics(self, articles: List[Dict]) -> Dict:
        """
        Get statistics about locations found in articles.
        
        Args:
            articles (List[Dict]): List of processed articles
            
        Returns:
            Dict: Statistics about locations
        """
        stats = {
            'total_articles': len(articles),
            'articles_with_locations': 0,
            'total_locations_found': 0,
            'location_types': {},
            'most_common_locations': {},
            'articles_by_continent': {}
        }
        
        location_counts = {}
        
        for article in articles:
            locations = article.get('extracted_locations', [])
            continent = article.get('continent', 'Unknown')
            
            if locations:
                stats['articles_with_locations'] += 1
                stats['total_locations_found'] += len(locations)
                
                # Count location types
                for loc in locations:
                    label = loc['label']
                    stats['location_types'][label] = stats['location_types'].get(label, 0) + 1
                    
                    # Count specific locations
                    location_text = loc['text'].lower()
                    location_counts[location_text] = location_counts.get(location_text, 0) + 1
                
                # Count articles by continent
                stats['articles_by_continent'][continent] = stats['articles_by_continent'].get(continent, 0) + 1
        
        # Get most common locations (top 10)
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        stats['most_common_locations'] = dict(sorted_locations[:10])
        
        return stats
    
    def find_articles_by_location(self, articles: List[Dict], location_name: str) -> List[Dict]:
        """
        Find articles that mention a specific location.
        
        Args:
            articles (List[Dict]): List of processed articles
            location_name (str): Name of the location to search for
            
        Returns:
            List[Dict]: Articles that mention the location
        """
        matching_articles = []
        location_lower = location_name.lower()
        
        for article in articles:
            locations = article.get('extracted_locations', [])
            for loc in locations:
                if location_lower in loc['text'].lower() or loc['text'].lower() in location_lower:
                    matching_articles.append(article)
                    break
        
        return matching_articles

# Global instance for easy access
ner_processor = NERProcessor() 

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def process_and_store_articles_with_ner(articles, mongo_uri, collection_name="news_by_location"):
    client = MongoClient(mongo_uri)
    db = client.get_default_database()  # This will use the DB from the URI
    collection = db[collection_name]
    for article in articles:
        url = article.get('url')
        country_code = article.get('country') or article.get('source_country')
        full_text = scrape_article_text(url) if url else None
        if full_text:
            entities = extract_entities(full_text)
            coordinates = get_country_coordinates(country_code) if country_code else None
            article['full_text'] = full_text
            article['entities'] = entities
            article['country_code'] = country_code
            if coordinates:
                article['longitude'] = coordinates[1]
                article['latitude'] = coordinates[0]
                article['coordinates'] = coordinates
            else:
                article['longitude'] = None
                article['latitude'] = None
                article['coordinates'] = None
        else:
            article['full_text'] = None
            article['entities'] = []
            article['country_code'] = country_code if country_code else None
            article['longitude'] = None
            article['latitude'] = None
            article['coordinates'] = None
        article.pop('_id', None)  # Remove the _id field if it exists
        collection.insert_one(article)
        print(f"Stored article with NER and location (may be null) for {article.get('url')} in {collection_name}") 

