#!/usr/bin/env python3
"""
Script to fetch 9 news stories from each continent and save them to MongoDB.
This is designed to efficiently use your daily API quota.
"""

from utility import fetch_all_continents_news
from flask import Flask
from flask_pymongo import PyMongo
import json

# Set up Flask app for MongoDB connection
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/news_world_database"
mongo = PyMongo(app)

def main():
    """Fetch 9 articles from each continent and save to MongoDB."""
    print("🌍 NEWS FETCHING SCRIPT")
    print("=" * 50)
    print("This will fetch 9 articles from each continent:")
    print("- Americas")
    print("- Europe") 
    print("- Asia")
    print("- Africa")
    print("- Oceania")
    print("=" * 50)
    print("Total API requests: 45 (9 per continent)")
    print("Make sure MongoDB is running!")
    print("=" * 50)
    
    # Confirm before proceeding
    response = input("\nProceed? (y/n): ").lower().strip()
    if response != 'y':
        print("Cancelled.")
        return
    
    try:
        with app.app_context():
            print("\n🚀 Starting fetch process...")
            
            # Fetch all continents (9 articles each)
            results = fetch_all_continents_news(mongo.db, articles_per_continent=9)
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 FINAL SUMMARY:")
            print("=" * 50)
            
            total_articles = 0
            for continent, articles in results.items():
                print(f"{continent}: {len(articles)} articles")
                total_articles += len(articles)
            
            print(f"\nTotal articles saved: {total_articles}")
            print("Database: news_world_database")
            print("Collection: news_by_location")
            
            # Show sample articles
            print("\n📰 Sample articles saved:")
            print("-" * 30)
            for continent, articles in results.items():
                if articles:
                    sample = articles[0]
                    print(f"{continent}: {sample.get('title', 'No title')[:60]}...")
                    print(f"  From: {sample.get('source_country', 'Unknown')}")
                    print(f"  Source: {sample.get('source', {}).get('name', 'Unknown')}")
                    print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure MongoDB is running and your API key is valid.")

if __name__ == "__main__":
    main() 