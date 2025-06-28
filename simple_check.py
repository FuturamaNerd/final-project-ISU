#!/usr/bin/env python3
"""
Simple script to check news_by_location collection.
"""

from pymongo import MongoClient

try:
    # Connect to MongoDB
    client = MongoClient('localhost', 27017)
    db = client['news_world_database']
    
    print("🔍 CHECKING NEWS_BY_LOCATION COLLECTION")
    print("=" * 50)
    
    # Check if collection exists
    if 'news_by_location' in db.list_collection_names():
        count = db.news_by_location.count_documents({})
        print(f"Total documents: {count}")
        
        if count > 0:
            # Get first document
            doc = db.news_by_location.find_one()
            print(f"\n📄 First document:")
            print(f"  ID: {doc.get('_id')}")
            print(f"  Title: {doc.get('title', 'No title')}")
            print(f"  Country: {doc.get('source_country', 'Unknown')}")
            print(f"  Source: {doc.get('source', {}).get('name', 'Unknown')}")
            print(f"  URL: {doc.get('url', 'No URL')}")
        else:
            print("❌ No documents found")
    else:
        print("❌ news_by_location collection does not exist")
        
    # List all collections
    print(f"\nAll collections: {db.list_collection_names()}")
    
except Exception as e:
    print(f"❌ Error: {e}")

finally:
    if 'client' in locals():
        client.close() 