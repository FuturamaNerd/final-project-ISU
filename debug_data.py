#!/usr/bin/env python3
"""
Debug script to check data availability and API endpoint
"""

import sqlite3
from flask import Flask
from flask_pymongo import PyMongo
import json

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/news_db'
mongo = PyMongo(app)

def check_mongodb_data():
    """Check NewsAPI data in MongoDB"""
    print("=== MongoDB (NewsAPI) Data ===")
    try:
        with app.app_context():
            articles = list(mongo.db.news_by_location.find().limit(5))
            print(f"Found {len(articles)} NewsAPI articles")
            
            if articles:
                print("Sample article:")
                sample = articles[0]
                print(f"  Title: {sample.get('title', 'No title')}")
                print(f"  Source: {sample.get('source', {}).get('name', 'Unknown')}")
                print(f"  Country: {sample.get('source_country', 'Unknown')}")
                print(f"  Has coordinates: {bool(sample.get('coordinates'))}")
                if sample.get('coordinates'):
                    print(f"  Coordinates: {sample['coordinates']}")
                print(f"  Has extracted_locations: {bool(sample.get('extracted_locations'))}")
            else:
                print("No NewsAPI articles found!")
    except Exception as e:
        print(f"Error accessing MongoDB: {e}")

def check_sqlite_data():
    """Check GDELT data in SQLite"""
    print("\n=== SQLite (GDELT) Data ===")
    try:
        conn = sqlite3.connect('gdelt_events.db')
        c = conn.cursor()
        
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gdelt_events'")
        if not c.fetchone():
            print("GDELT events table does not exist!")
            return
        
        # Count total events
        c.execute("SELECT COUNT(*) FROM gdelt_events")
        total_count = c.fetchone()[0]
        print(f"Found {total_count} GDELT events")
        
        # Get sample events
        events = c.execute('''
            SELECT event_id, date, event_code, goldstein, actor1_name, actor1_country, 
                   actor2_name, actor2_country, latitude, longitude, location_name, 
                   continent, source_url FROM gdelt_events LIMIT 5
        ''').fetchall()
        
        if events:
            print("Sample GDELT event:")
            sample = events[0]
            print(f"  Event ID: {sample[0]}")
            print(f"  Date: {sample[1]}")
            print(f"  Actor1: {sample[4]} ({sample[5]})")
            print(f"  Actor2: {sample[6]} ({sample[7]})")
            print(f"  Coordinates: [{sample[8]}, {sample[9]}]")
            print(f"  Location: {sample[10]}")
            print(f"  Continent: {sample[11]}")
            print(f"  Source URL: {sample[12]}")
        else:
            print("No GDELT events found!")
        
        conn.close()
    except Exception as e:
        print(f"Error accessing SQLite: {e}")

def test_api_endpoint():
    """Test the API endpoint"""
    print("\n=== Testing API Endpoint ===")
    try:
        with app.app_context():
            # Simulate the API endpoint logic
            events = []
            
            # Get NewsAPI events
            newsapi_events = list(mongo.db.news_by_location.find().limit(10))
            for event in newsapi_events:
                event['_id'] = str(event['_id'])
                event['data_source'] = 'newsapi'
                events.append(event)
            
            # Get GDELT events
            conn = sqlite3.connect('gdelt_events.db')
            c = conn.cursor()
            gdelt_events = c.execute('''
                SELECT event_id, date, event_code, goldstein, actor1_name, actor1_country, 
                       actor2_name, actor2_country, latitude, longitude, location_name, 
                       continent, source_url FROM gdelt_events LIMIT 10
            ''').fetchall()
            conn.close()
            
            for event in gdelt_events:
                events.append({
                    'event_id': event[0],
                    'date': event[1],
                    'event_code': event[2],
                    'goldstein': event[3],
                    'actor1_name': event[4],
                    'actor1_country': event[5],
                    'actor2_name': event[6],
                    'actor2_country': event[7],
                    'latitude': event[8],
                    'longitude': event[9],
                    'location_name': event[10],
                    'continent': event[11],
                    'source_url': event[12],
                    'data_source': 'gdelt'
                })
            
            print(f"API would return {len(events)} total events")
            print(f"  - NewsAPI: {len([e for e in events if e.get('data_source') == 'newsapi'])}")
            print(f"  - GDELT: {len([e for e in events if e.get('data_source') == 'gdelt'])}")
            
            # Check for events with coordinates
            events_with_coords = []
            for event in events:
                if event.get('data_source') == 'gdelt':
                    if event.get('latitude') and event.get('longitude'):
                        events_with_coords.append(event)
                else:  # NewsAPI
                    if event.get('coordinates'):
                        events_with_coords.append(event)
            
            print(f"Events with coordinates: {len(events_with_coords)}")
            
            if events_with_coords:
                print("Sample event with coordinates:")
                sample = events_with_coords[0]
                if sample.get('data_source') == 'gdelt':
                    print(f"  GDELT: [{sample['latitude']}, {sample['longitude']}] - {sample['actor1_name']}")
                else:
                    print(f"  NewsAPI: {sample['coordinates']} - {sample.get('title', 'No title')}")
            
    except Exception as e:
        print(f"Error testing API endpoint: {e}")

if __name__ == "__main__":
    check_mongodb_data()
    check_sqlite_data()
    test_api_endpoint() 