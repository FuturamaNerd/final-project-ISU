#!/usr/bin/env python3
"""
Script to check the dummy data in the dummy_news collection.
"""

from flask import Flask
from flask_pymongo import PyMongo
import json

# Set up Flask app for MongoDB connection
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/news_world_database"
mongo = PyMongo(app)

def check_dummy_data():
    """Check what's in the dummy_news collection."""
    
    try:
        with app.app_context():
            print("🔍 CHECKING DUMMY NEWS DATA")
            print("=" * 50)
            
            # Check if dummy_news collection exists
            collections = mongo.db.list_collection_names()
            print(f"Available collections: {collections}")
            
            if 'dummy_news' in collections:
                print("\n📰 DUMMY_NEWS COLLECTION:")
                print("-" * 30)
                
                # Count documents
                count = mongo.db.dummy_news.count_documents({})
                print(f"Total documents: {count}")
                
                if count > 0:
                    # Get all documents
                    documents = list(mongo.db.dummy_news.find())
                    
                    # Group by continent
                    continents = {}
                    for doc in documents:
                        continent = doc.get('continent', 'Unknown')
                        if continent not in continents:
                            continents[continent] = []
                        continents[continent].append(doc)
                    
                    print(f"\n📊 ARTICLES BY CONTINENT:")
                    print("-" * 30)
                    for continent, articles in continents.items():
                        print(f"{continent}: {len(articles)} articles")
                        
                        # Show sample article for each continent
                        if articles:
                            sample = articles[0]
                            print(f"  Sample: {sample.get('title', 'No title')[:50]}...")
                            print(f"  Country: {sample.get('source_country', 'Unknown')}")
                            print(f"  Source: {sample.get('source', {}).get('name', 'Unknown')}")
                            print()
                    
                    # Show all articles in detail
                    print("📄 ALL ARTICLES DETAIL:")
                    print("-" * 30)
                    for i, doc in enumerate(documents, 1):
                        print(f"\nArticle {i}:")
                        print(f"  Title: {doc.get('title', 'No title')}")
                        print(f"  Country: {doc.get('source_country', 'Unknown')}")
                        print(f"  Continent: {doc.get('continent', 'Unknown')}")
                        print(f"  Source: {doc.get('source', {}).get('name', 'Unknown')}")
                        print(f"  URL: {doc.get('url', 'No URL')}")
                        print(f"  Description: {doc.get('description', 'No description')[:100]}...")
                else:
                    print("❌ No documents found in dummy_news collection")
            else:
                print("❌ dummy_news collection does not exist")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_dummy_data() 