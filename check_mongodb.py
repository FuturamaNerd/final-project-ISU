#!/usr/bin/env python3
"""
Script to check what's currently in the MongoDB database.
"""

from flask import Flask
from flask_pymongo import PyMongo
import json

# Set up Flask app for MongoDB connection
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/news_world_database"
mongo = PyMongo(app)

def check_database():
    """Check what's in the MongoDB database."""
    
    try:
        with app.app_context():
            print("🔍 CHECKING MONGODB DATABASE")
            print("=" * 50)
            
            # Check if database exists
            print(f"Database name: {mongo.db.name}")
            
            # List all collections
            collections = mongo.db.list_collection_names()
            print(f"Collections: {collections}")
            
            # Check the news_by_location collection
            if 'news_by_location' in collections:
                print("\n📰 NEWS_BY_LOCATION COLLECTION:")
                print("-" * 30)
                
                # Count documents
                count = mongo.db.news_by_location.count_documents({})
                print(f"Total documents: {count}")
                
                if count > 0:
                    # Get all documents
                    documents = list(mongo.db.news_by_location.find())
                    
                    for i, doc in enumerate(documents, 1):
                        print(f"\n📄 Document {i}:")
                        print(f"  ID: {doc.get('_id')}")
                        print(f"  Title: {doc.get('title', 'No title')[:60]}...")
                        print(f"  Country: {doc.get('source_country', 'Unknown')}")
                        print(f"  Continent: {doc.get('continent', 'Unknown')}")
                        print(f"  Source: {doc.get('source', {}).get('name', 'Unknown')}")
                        print(f"  Saved at: {doc.get('saved_at', 'Unknown')}")
                        print(f"  URL: {doc.get('url', 'No URL')[:50]}...")
                else:
                    print("❌ No documents found in news_by_location collection")
            else:
                print("❌ news_by_location collection does not exist")
            
            # Check if there are any other collections with data
            print("\n🔍 CHECKING ALL COLLECTIONS:")
            print("-" * 30)
            for collection_name in collections:
                count = mongo.db[collection_name].count_documents({})
                print(f"{collection_name}: {count} documents")
                
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        print("Make sure MongoDB is running!")

if __name__ == "__main__":
    check_database() 