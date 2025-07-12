#!/usr/bin/env python3
"""
Script to process existing MongoDB articles with Named Entity Recognition (NER).
This will extract location entities from article content and update the database.
"""

from pymongo import MongoClient
from utility.ner_processor import ner_processor
import json
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["news_world_database"]

def process_existing_articles():
    """Process all existing articles in the news_by_location collection with NER."""
    
    try:
        print("🔍 PROCESSING ARTICLES WITH NER")
        print("=" * 50)
        
        # Get all articles from the collection
        articles = list(db.news_by_location.find())
        print(f"Found {len(articles)} articles to process")
        
        if not articles:
            print("❌ No articles found in the database")
            return
        
        # Process articles with NER
        print("\n🚀 Starting NER processing...")
        processed_articles = ner_processor.process_multiple_articles(articles)
        
        # Update articles in database
        print("\n💾 Updating articles in database...")
        updated_count = 0
        
        for article in processed_articles:
            # Remove MongoDB ObjectId for update
            article_id = article.pop('_id', None)
            
            if article_id:
                # Update the document
                result = db.news_by_location.update_one(
                    {'_id': article_id},
                    {'$set': {
                        'extracted_locations': article.get('extracted_locations', []),
                        'location_count': article.get('location_count', 0),
                        'primary_location': article.get('primary_location'),
                        'ner_processed_at': datetime.utcnow()
                    }}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
        
        print(f"✅ Successfully updated {updated_count}/{len(articles)} articles")
        
        # Get basic statistics
        print("\n📊 LOCATION STATISTICS:")
        print("-" * 30)
        
        total_articles = len(processed_articles)
        articles_with_locations = sum(1 for article in processed_articles if article.get('location_count', 0) > 0)
        total_locations = sum(article.get('location_count', 0) for article in processed_articles)
        
        print(f"Total articles: {total_articles}")
        print(f"Articles with locations: {articles_with_locations}")
        print(f"Total locations found: {total_locations}")
        
        # Count location types
        location_types = {}
        for article in processed_articles:
            for loc in article.get('extracted_locations', []):
                label = loc.get('label', 'Unknown')
                location_types[label] = location_types.get(label, 0) + 1
        
        print(f"\nLocation types found:")
        for loc_type, count in location_types.items():
            print(f"  {loc_type}: {count}")
        
        # Show sample processed articles
        print("\n📰 SAMPLE PROCESSED ARTICLES:")
        print("-" * 30)
        for i, article in enumerate(processed_articles[:3]):
            print(f"\nArticle {i+1}:")
            print(f"  Title: {article.get('title', 'No title')[:60]}...")
            print(f"  Primary Location: {article.get('primary_location', 'None')}")
            print(f"  Location Count: {article.get('location_count', 0)}")
            if article.get('extracted_locations'):
                print(f"  Locations: {', '.join([loc['text'] for loc in article['extracted_locations'][:3]])}")
        
    except Exception as e:
        print(f"❌ Error processing articles: {e}")

def search_articles_by_location(location_name: str):
    """Search for articles that mention a specific location."""
    
    try:
        print(f"🔍 SEARCHING FOR ARTICLES MENTIONING: {location_name}")
        print("=" * 50)
        
        # Get all articles
        articles = list(db.news_by_location.find())
        
        if not articles:
            print("❌ No articles found in the database")
            return
        
        # Process articles if they haven't been processed yet
        processed_articles = []
        for article in articles:
            if 'extracted_locations' not in article:
                processed_article = ner_processor.process_article(article)
                processed_articles.append(processed_article)
            else:
                processed_articles.append(article)
        
        # Find matching articles
        matching_articles = []
        location_lower = location_name.lower()
        for article in processed_articles:
            locations = article.get('extracted_locations', [])
            for loc in locations:
                if location_lower in loc['text'].lower() or loc['text'].lower() in location_lower:
                    matching_articles.append(article)
                    break
        
        print(f"Found {len(matching_articles)} articles mentioning '{location_name}'")
        
        for i, article in enumerate(matching_articles):
            print(f"\n📄 Article {i+1}:")
            print(f"  Title: {article.get('title', 'No title')}")
            print(f"  Source: {article.get('source', {}).get('name', 'Unknown')}")
            print(f"  Country: {article.get('source_country', 'Unknown')}")
            print(f"  URL: {article.get('url', 'No URL')}")
            
            # Show matching locations
            locations = article.get('extracted_locations', [])
            matching_locs = [loc for loc in locations if location_name.lower() in loc['text'].lower()]
            if matching_locs:
                print(f"  Matching locations: {', '.join([loc['text'] for loc in matching_locs])}")
        
    except Exception as e:
        print(f"❌ Error searching articles: {e}")

def main():
    """Main function with interactive menu."""
    
    print("🌍 NEWS ARTICLE NER PROCESSOR")
    print("=" * 50)
    print("1. Process all articles with NER")
    print("2. Search articles by location")
    print("3. Exit")
    print("=" * 50)
    
    while True:
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == '1':
            process_existing_articles()
        elif choice == '2':
            location = input("Enter location name to search for: ").strip()
            if location:
                search_articles_by_location(location)
            else:
                print("❌ Please enter a valid location name")
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main() 