#!/usr/bin/env python3
"""
Debug script to see what data is being passed to the template.
"""

from flask import Flask
from flask_pymongo import PyMongo
import json

# Set up Flask app for MongoDB connection
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/news_world_database"
mongo = PyMongo(app)

def debug_continent_data(continent):
    """Debug the data for a specific continent."""
    
    try:
        with app.app_context():
            print(f"🔍 DEBUGGING DATA FOR {continent.upper()}")
            print("=" * 50)
            
            # Get news stories for the specified continent
            news_stories = list(mongo.db.dummy_news.find({'continent': continent}))
            
            print(f"Found {len(news_stories)} articles for {continent}")
            
            if news_stories:
                # Show the first article in detail
                first_article = news_stories[0]
                print(f"\n📄 FIRST ARTICLE DETAIL:")
                print("-" * 30)
                print(f"Title: {first_article.get('title')}")
                print(f"Description: {first_article.get('description')}")
                print(f"URL: {first_article.get('url')}")
                print(f"Author: {first_article.get('author')}")
                print(f"Source: {first_article.get('source')}")
                print(f"Source Country: {first_article.get('source_country')}")
                print(f"Continent: {first_article.get('continent')}")
                print(f"Published At: {first_article.get('publishedAt')}")
                print(f"URL To Image: {first_article.get('urlToImage')}")
                print(f"Content: {first_article.get('content')}")
                
                # Show all articles briefly
                print(f"\n📰 ALL ARTICLES FOR {continent}:")
                print("-" * 30)
                for i, article in enumerate(news_stories, 1):
                    print(f"{i}. Title: {article.get('title', 'NO TITLE')}")
                    print(f"   Description: {article.get('description', 'NO DESCRIPTION')[:50]}...")
                    print(f"   URL: {article.get('url', 'NO URL')}")
                    print()
            else:
                print(f"❌ No articles found for {continent}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_continent_data('Americas')
    print("\n" + "="*60 + "\n")
    debug_continent_data('Oceania') 