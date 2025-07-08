import requests
import json
import random
import os
from typing import Dict, List, Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utility.config import NEWS_API_KEY

def load_country_mapping() -> Dict[str, str]:
    """Load the country code to continent mapping from JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), 'countryToContinent.json')
    with open(json_path, 'r') as f:
        return json.load(f)

def load_country_coordinates() -> Dict[str, List[float]]:
    """Load country coordinates from JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), 'countryCoordinates.json')
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Country coordinates file not found at {json_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in country coordinates file")
        return {}

def get_country_coordinates(country_code: str) -> List[float]:
    """Get coordinates for a country code."""
    coordinates = load_country_coordinates()
    return coordinates.get(country_code, [39.8283, -98.5795])  # Default to US center

def get_countries_by_continent(continent: str) -> List[str]:
    """Get all country codes for a given continent."""
    country_mapping = load_country_mapping()
    countries = [code for code, cont in country_mapping.items() if cont == continent]
    return countries

def get_news_api_key() -> str:
    """Get the NewsAPI key from configuration."""
    return NEWS_API_KEY

def fetch_random_country_news(continent: str) -> Optional[Dict]:
    """
    Randomly pick a country from the specified continent and fetch one news story.
    
    Args:
        continent (str): One of 'Americas', 'Europe', 'Asia', 'Africa', 'Oceania'
    
    Returns:
        dict: News article data or None if no article found
    """
    # Validate continent
    valid_continents = ['Americas', 'Europe', 'Asia', 'Africa', 'Oceania']
    if continent not in valid_continents:
        raise ValueError(f"Continent must be one of: {valid_continents}")
    
    # Get countries for the continent
    countries = get_countries_by_continent(continent)
    if not countries:
        raise ValueError(f"No countries found for continent: {continent}")
    
    # Randomly select a country
    selected_country = random.choice(countries)
    
    # Get API key
    api_key = get_news_api_key()
    
    # Fetch news from NewsAPI
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': selected_country.lower(),
        'apiKey': api_key,
        'pageSize': 1  # Get only one article
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == 'ok' and data['articles']:
            article = data['articles'][0]
            # Add country info to the article data
            article['source_country'] = selected_country
            article['continent'] = continent
            
            # Add country coordinates for map positioning
            coordinates = get_country_coordinates(selected_country)
            article['coordinates'] = coordinates
            article['location_precision'] = 'country'
            article['data_source'] = 'newsapi'
            
            return article
        else:
            print(f"No articles found for country: {selected_country}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {selected_country}: {e}")
        return None
    except KeyError as e:
        print(f"Unexpected response format: {e}")
        return None

def fetch_multiple_continent_news(continent: str, count: int = 9) -> List[Dict]:
    """
    Fetch multiple news stories from a continent by trying different countries.
    
    Args:
        continent (str): One of 'Americas', 'Europe', 'Asia', 'Africa', 'Oceania'
        count (int): Number of articles to fetch (default: 9)
    
    Returns:
        list: List of news article data
    """
    articles = []
    countries = get_countries_by_continent(continent)
    
    if not countries:
        raise ValueError(f"No countries found for continent: {continent}")
    
    # Shuffle countries to get variety
    random.shuffle(countries)
    
    api_key = get_news_api_key()
    url = "https://newsapi.org/v2/top-headlines"
    
    for country in countries:
        if len(articles) >= count:
            break
            
        params = {
            'country': country.lower(),
            'apiKey': api_key,
            'pageSize': 1
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
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
                
                articles.append(article)
                print(f"✅ Fetched article from {country} ({len(articles)}/{count})")
            else:
                print(f"⚠️  No articles found for {country}")
                
        except Exception as e:
            print(f"❌ Error fetching from {country}: {e}")
            continue
    
    print(f"📊 Total articles fetched for {continent}: {len(articles)}")
    return articles

def save_news_to_mongodb(article_data: Dict, mongo_db) -> bool:
    """
    Save the news article to MongoDB.
    
    Args:
        article_data (dict): The article data to save
        mongo_db: MongoDB database instance
    
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Add timestamp
        from datetime import datetime
        article_data['saved_at'] = datetime.utcnow()
        
        # Insert into MongoDB
        result = mongo_db.news_by_location.insert_one(article_data)
        print(f"💾 Saved article with ID: {result.inserted_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to MongoDB: {e}")
        return False

def fetch_and_save_continent_news(continent: str, mongo_db) -> Optional[Dict]:
    """
    Fetch a random news story from a continent and save it to MongoDB.
    
    Args:
        continent (str): The continent to fetch news from
        mongo_db: MongoDB database instance
    
    Returns:
        dict: The saved article data or None if failed
    """
    article = fetch_random_country_news(continent)
    if article:
        if save_news_to_mongodb(article, mongo_db):
            return article
    return None

def fetch_and_save_multiple_continent_news(continent: str, mongo_db, count: int = 9) -> List[Dict]:
    """
    Fetch multiple news stories from a continent and save them all to MongoDB.
    
    Args:
        continent (str): The continent to fetch news from
        mongo_db: MongoDB database instance
        count (int): Number of articles to fetch (default: 9)
    
    Returns:
        list: List of saved article data
    """
    print(f"\n🌍 Fetching {count} articles from {continent}...")
    articles = fetch_multiple_continent_news(continent, count)
    
    saved_articles = []
    for article in articles:
        if save_news_to_mongodb(article, mongo_db):
            saved_articles.append(article)
    
    print(f"📈 Successfully saved {len(saved_articles)}/{len(articles)} articles for {continent}")
    return saved_articles

def fetch_all_continents_news(mongo_db, articles_per_continent: int = 9) -> Dict[str, List[Dict]]:
    """
    Fetch news from all continents and save to MongoDB.
    
    Args:
        mongo_db: MongoDB database instance
        articles_per_continent (int): Number of articles per continent (default: 9)
    
    Returns:
        dict: Dictionary with continent as key and list of saved articles as value
    """
    continents = ['Americas', 'Europe', 'Asia', 'Africa', 'Oceania']
    all_results = {}
    
    print(f"🚀 Starting to fetch {articles_per_continent} articles from each continent...")
    print(f"📊 Total API requests needed: {len(continents) * articles_per_continent}")
    
    for continent in continents:
        saved_articles = fetch_and_save_multiple_continent_news(continent, mongo_db, articles_per_continent)
        all_results[continent] = saved_articles
    
    total_saved = sum(len(articles) for articles in all_results.values())
    print(f"\n🎉 COMPLETED! Total articles saved: {total_saved}")
    
    return all_results
