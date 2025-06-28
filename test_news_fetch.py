#!/usr/bin/env python3
"""
Test script for the news fetching functionality.
This script demonstrates how to use the fetch_random_country_news function.
"""

from utility import fetch_random_country_news, get_countries_by_continent, fetch_and_save_continent_news
import json
from flask import Flask
from flask_pymongo import PyMongo

# Set up Flask app for MongoDB connection
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/news_world_database"
mongo = PyMongo(app)

def test_continent_countries():
    """Test getting countries for each continent."""
    continents = ['Americas', 'Europe', 'Asia', 'Africa', 'Oceania']
    
    for continent in continents:
        countries = get_countries_by_continent(continent)
        print(f"{continent}: {len(countries)} countries")
        print(f"Sample countries: {countries[:5]}")
        print("-" * 50)

def test_news_fetch():
    """Test fetching news from each continent."""
    continents = ['Americas', 'Europe', 'Asia', 'Africa', 'Oceania']
    
    for continent in continents:
        print(f"\nFetching news from {continent}...")
        try:
            article = fetch_random_country_news(continent)
            if article:
                print(f"✅ Success! Found article from {article.get('source_country', 'Unknown')}")
                print(f"Title: {article.get('title', 'No title')}")
                print(f"Source: {article.get('source', {}).get('name', 'Unknown')}")
                print(f"URL: {article.get('url', 'No URL')}")
            else:
                print(f"❌ No article found for {continent}")
        except Exception as e:
            print(f"❌ Error fetching news for {continent}: {e}")
        print("-" * 50)

def test_news_fetch_and_save():
    """Test fetching news from each continent AND saving to MongoDB."""
    continents = ['Americas', 'Europe', 'Asia', 'Africa', 'Oceania']
    
    with app.app_context():
        for continent in continents:
            print(f"\nFetching and saving news from {continent}...")
            try:
                saved_article = fetch_and_save_continent_news(continent, mongo.db)
                if saved_article:
                    print(f"✅ Success! Saved article from {saved_article.get('source_country', 'Unknown')}")
                    print(f"Title: {saved_article.get('title', 'No title')}")
                    print(f"MongoDB ID: {saved_article.get('_id', 'No ID')}")
                else:
                    print(f"❌ Failed to fetch or save article for {continent}")
            except Exception as e:
                print(f"❌ Error: {e}")
            print("-" * 50)

if __name__ == "__main__":
    print("Testing continent country mapping...")
    test_continent_countries()
    
    print("\n" + "="*60)
    print("Testing news fetching (without saving)...")
    test_news_fetch()
    
    print("\n" + "="*60)
    print("Testing news fetching AND saving to MongoDB...")
    test_news_fetch_and_save() 