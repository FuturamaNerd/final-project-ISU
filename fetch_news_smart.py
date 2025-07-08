#!/usr/bin/env python3
"""
Smart news fetching script that handles rate limits and focuses on major countries.
"""

from utility.api_client import save_news_to_mongodb
from flask import Flask
from flask_pymongo import PyMongo
import time
import random
import json
import os
from utility.config import NEWS_API_KEY

# Set up Flask app for MongoDB connection
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/news_world_database"
mongo = PyMongo(app)

# Major countries that are more likely to have news
MAJOR_COUNTRIES = {
    'Americas': ['US', 'CA', 'BR', 'MX', 'AR', 'CL', 'CO', 'PE', 'VE'],
    'Europe': ['GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'SE', 'NO', 'CH'],
    'Asia': ['CN', 'JP', 'IN', 'KR', 'SG', 'AU', 'TH', 'MY', 'ID'],
    'Africa': ['ZA', 'EG', 'NG', 'KE', 'GH', 'MA', 'TN', 'DZ', 'ET'],
    'Oceania': ['AU', 'NZ', 'FJ', 'PG', 'NC', 'VU', 'SB', 'TO', 'WS']
}

def load_country_coordinates():
    """Load country coordinates from JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), 'utility', 'countryCoordinates.json')
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Country coordinates file not found at {json_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in country coordinates file")
        return {}

def get_country_coordinates(country_code):
    """Get coordinates for a country code."""
    coordinates = load_country_coordinates()
    return coordinates.get(country_code, [39.8283, -98.5795])  # Default to US center

def fetch_continent_news_smart(continent: str, mongo_db, count: int = 9, delay: float = 1.0):
    """
    Fetch news from a continent using major countries and rate limiting.
    
    Args:
        continent (str): The continent to fetch from
        mongo_db: MongoDB database instance
        count (int): Number of articles to fetch
        delay (float): Delay between requests in seconds
    """
    print(f"\n🌍 Fetching {count} articles from {continent} (smart mode)...")
    
    countries = MAJOR_COUNTRIES.get(continent, [])
    if not countries:
        print(f"❌ No major countries defined for {continent}")
        return []
    
    saved_articles = []
    attempts = 0
    max_attempts = count * 3  # Try up to 3x the target count
    
    for country in countries:
        if len(saved_articles) >= count or attempts >= max_attempts:
            break
            
        print(f"  Trying {country}...")
        
        try:
            # Fetch article for this specific country
            article = fetch_single_country_news(country, continent)
            
            if article:
                # Save to MongoDB
                if save_news_to_mongodb(article, mongo_db):
                    saved_articles.append(article)
                    print(f"  ✅ Saved article from {country} ({len(saved_articles)}/{count})")
                else:
                    print(f"  ❌ Failed to save article from {country}")
            else:
                print(f"  ⚠️  No articles found for {country}")
            
            # Add delay to avoid rate limiting
            time.sleep(delay)
            attempts += 1
            
        except Exception as e:
            print(f"  ❌ Error with {country}: {e}")
            time.sleep(delay * 2)  # Longer delay on error
            attempts += 1
            continue
    
    print(f"📊 Successfully saved {len(saved_articles)}/{count} articles for {continent}")
    return saved_articles

def fetch_single_country_news(country: str, continent: str):
    """Fetch a single article from a specific country."""
    import requests
    
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': country.lower(),
        'apiKey': NEWS_API_KEY,
        'pageSize': 1
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'ok' and data['articles']:
                article = data['articles'][0]
                article['source_country'] = country
                article['continent'] = continent
                
                # Add country coordinates for map positioning
                coordinates = get_country_coordinates(country)
                article['coordinates'] = coordinates
                article['location_precision'] = 'country'
                article['data_source'] = 'newsapi'
                
                print(f"    📍 Added coordinates for {country}: {coordinates}")
                return article
        elif response.status_code == 429:
            print(f"  ⏳ Rate limited for {country}, waiting...")
            time.sleep(5)  # Wait 5 seconds on rate limit
        else:
            print(f"  ❌ HTTP {response.status_code} for {country}")
            
    except Exception as e:
        print(f"  ❌ Request failed for {country}: {e}")
    
    return None

def main():
    """Main function to fetch news from all continents."""
    print("🌍 SMART NEWS FETCHING SCRIPT")
    print("=" * 50)
    print("This will fetch articles from major countries:")
    for continent, countries in MAJOR_COUNTRIES.items():
        print(f"- {continent}: {', '.join(countries[:5])}...")
    print("=" * 50)
    print("Features:")
    print("- Rate limiting protection")
    print("- Focuses on major countries")
    print("- Graceful error handling")
    print("=" * 50)
    
    # Confirm before proceeding
    response = input("\nProceed? (y/n): ").lower().strip()
    if response != 'y':
        print("Cancelled.")
        return
    
    try:
        with app.app_context():
            print("\n🚀 Starting smart fetch process...")
            
            all_results = {}
            total_saved = 0
            
            for continent in MAJOR_COUNTRIES.keys():
                saved_articles = fetch_continent_news_smart(continent, mongo.db, count=5, delay=1.5)
                all_results[continent] = saved_articles
                total_saved += len(saved_articles)
                
                # Add delay between continents
                if continent != list(MAJOR_COUNTRIES.keys())[-1]:
                    print("  ⏳ Waiting between continents...")
                    time.sleep(3)
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 FINAL SUMMARY:")
            print("=" * 50)
            
            for continent, articles in all_results.items():
                print(f"{continent}: {len(articles)} articles")
            
            print(f"\nTotal articles saved: {total_saved}")
            print("Database: news_world_database")
            print("Collection: news_by_location")
            
            # Show sample articles
            print("\n📰 Sample articles saved:")
            print("-" * 30)
            for continent, articles in all_results.items():
                if articles:
                    sample = articles[0]
                    print(f"{continent}: {sample.get('title', 'No title')[:60]}...")
                    print(f"  From: {sample.get('source_country', 'Unknown')}")
                    print(f"  Source: {sample.get('source', {}).get('name', 'Unknown')}")
                    print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 