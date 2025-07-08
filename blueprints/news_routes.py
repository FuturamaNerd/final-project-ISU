from flask import Blueprint, jsonify, current_app
from flask_pymongo import PyMongo
import sqlite3

# Create the blueprint
news_bp = Blueprint('news', __name__)

# MongoDB connection (will be configured in main app)
mongo = None

def init_mongo(mongo_instance):
    """Initialize MongoDB connection for the blueprint"""
    global mongo
    mongo = mongo_instance

@news_bp.route('/api/events/all')
def get_all_events():
    """API endpoint to get all events from both NewsAPI and GDELT."""
    try:
        events = []
        
        # Get NewsAPI events from MongoDB
        try:
            newsapi_events = list(mongo.db.news_by_location.find().limit(50))
            for event in newsapi_events:
                # Convert MongoDB ObjectId to string
                event['_id'] = str(event['_id'])
                event['data_source'] = 'newsapi'
                events.append(event)
            print(f"Found {len(newsapi_events)} NewsAPI events")
        except Exception as e:
            print(f"Error accessing MongoDB: {e}")
            # Continue with GDELT events even if MongoDB fails
        
        # Get GDELT events from SQLite
        try:
            conn = sqlite3.connect('gdelt_events.db')
            c = conn.cursor()
            gdelt_events = c.execute('''
                SELECT event_id, date, event_code, goldstein, actor1_name, actor1_country, 
                       actor2_name, actor2_country, latitude, longitude, location_name, 
                       continent, source_url FROM gdelt_events LIMIT 50
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
            print(f"Found {len(gdelt_events)} GDELT events")
        except Exception as e:
            print(f"Error accessing SQLite: {e}")
        
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
