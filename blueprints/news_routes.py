from flask import Blueprint, jsonify, current_app, request
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
    if mongo is None:
        return jsonify({'success': False, 'error': 'MongoDB is not initialized.'}), 500
    try:
        events = []
        
        # Get NewsAPI events from MongoDB
        try:
            newsapi_events = list(mongo.db.news_by_location.find())
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
                       continent, source_url, translated_title, translated_content, 
                       source_language, target_language, translation_confidence, 
                       sentiment_score, sentiment_magnitude, num_mentions, num_sources, 
                       avg_tone, event_root_code, event_base_code, quad_class, 
                       actor1_type1_code, actor1_type2_code, actor2_type1_code, 
                       actor2_type2_code, action_geo_type, action_geo_country, 
                       action_geo_adm1, action_geo_adm2, action_geo_lat, action_geo_long,
                       scraped_title
                FROM gdelt_events
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
                    # Translation fields
                    'translated_title': event[13],
                    'translated_content': event[14],
                    'source_language': event[15],
                    'target_language': event[16],
                    'translation_confidence': event[17],
                    'sentiment_score': event[18],
                    'sentiment_magnitude': event[19],
                    'num_mentions': event[20],
                    'num_sources': event[21],
                    'avg_tone': event[22],
                    # Additional GDELT fields
                    'event_root_code': event[23],
                    'event_base_code': event[24],
                    'quad_class': event[25],
                    'actor1_type1_code': event[26],
                    'actor1_type2_code': event[27],
                    'actor2_type1_code': event[28],
                    'actor2_type2_code': event[29],
                    'action_geo_type': event[30],
                    'action_geo_country': event[31],
                    'action_geo_adm1': event[32],
                    'action_geo_adm2': event[33],
                    'action_geo_lat': event[34],
                    'action_geo_long': event[35],
                    'scraped_title': event[36],
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

@news_bp.route('/api/newsapi')
def get_newsapi():
    if mongo is None:
        return jsonify({'success': False, 'error': 'MongoDB is not initialized.'}), 500
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(max(limit, 1), 200)  # Clamp between 1 and 200
        newsapi_events = list(mongo.db.news_by_location.find().limit(limit))
        for event in newsapi_events:
            event['_id'] = str(event['_id'])
        return jsonify({
            'success': True,
            'events': newsapi_events,
            'count': len(newsapi_events)
        })
    except Exception as e:
        print(f"Error in /api/newsapi: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@news_bp.route('/api/lucky/<continent>')
def get_lucky_story(continent):
    """Get a random news story from a specific continent."""
    if mongo is None:
        return jsonify({'success': False, 'error': 'MongoDB is not initialized.'}), 500
    
    try:
        import json
        import random
        
        # Load continent bounding boxes
        with open('continentBoundingBoxes.json', 'r', encoding='utf-8') as f:
            continent_boxes = json.load(f)
        
        # Map continent names to match the JSON file
        continent_mapping = {
            'Oceania': 'Australia (Oceania)',
            'Africa': 'Africa',
            'Asia': 'Asia', 
            'Europe': 'Europe',
            'Americas': 'Americas'
        }
        
        target_continent = continent_mapping.get(continent, continent)
        if target_continent not in continent_boxes:
            return jsonify({'success': False, 'error': f'Continent {continent} not found'}), 404
        
        bounds = continent_boxes[target_continent]
        
        # Get all stories with coordinates for this continent
        all_stories = []
        
        # Get NewsAPI stories
        try:
            all_newsapi = list(mongo.db.news_by_location.find({
                '$and': [
                    {'latitude': {'$exists': True, '$ne': None}},
                    {'longitude': {'$exists': True, '$ne': None}}
                ]
            }))
            
            for story in all_newsapi:
                lat = story.get('latitude')
                lon = story.get('longitude')
                
                if lat is not None and lon is not None:
                    if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                        bounds['lon_min'] <= lon <= bounds['lon_max']):
                        story['_id'] = str(story['_id'])
                        story['data_source'] = 'newsapi'
                        all_stories.append(story)
        except Exception as e:
            print(f"Error getting NewsAPI stories: {e}")
        
        # Get GDELT stories
        try:
            conn = sqlite3.connect('gdelt_events.db')
            c = conn.cursor()
            
            gdelt_query = '''
                SELECT event_id, date, event_code, goldstein, actor1_name, actor1_country, 
                       actor2_name, actor2_country, latitude, longitude, location_name, 
                       continent, source_url, translated_title, translated_content, 
                       source_language, target_language, translation_confidence, 
                       sentiment_score, sentiment_magnitude, num_mentions, num_sources, 
                       avg_tone, event_root_code, event_base_code, quad_class, scraped_title
                FROM gdelt_events 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            '''
            
            all_gdelt = c.execute(gdelt_query).fetchall()
            conn.close()
            
            for story in all_gdelt:
                lat = story[8]  # latitude
                lon = story[9]  # longitude
                
                if lat is not None and lon is not None:
                    if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                        bounds['lon_min'] <= lon <= bounds['lon_max']):
                        gdelt_story = {
                            'event_id': story[0],
                            'date': story[1],
                            'event_code': story[2],
                            'goldstein': story[3],
                            'actor1_name': story[4],
                            'actor1_country': story[5],
                            'actor2_name': story[6],
                            'actor2_country': story[7],
                            'latitude': story[8],
                            'longitude': story[9],
                            'location_name': story[10],
                            'continent': story[11],
                            'source_url': story[12],
                            'translated_title': story[13],
                            'translated_content': story[14],
                            'source_language': story[15],
                            'target_language': story[16],
                            'translation_confidence': story[17],
                            'sentiment_score': story[18],
                            'sentiment_magnitude': story[19],
                            'num_mentions': story[20],
                            'num_sources': story[21],
                            'avg_tone': story[22],
                            'event_root_code': story[23],
                            'event_base_code': story[24],
                            'quad_class': story[25],
                            'scraped_title': story[26],
                            'data_source': 'gdelt',
                            'title': story[26] if story[26] else (story[13] if story[13] else f'GDELT Event {story[0]}'),
                            'description': story[14][:200] + '...' if story[14] and len(story[14]) > 200 else (story[14] or 'No description available'),
                            'url': story[12] or '#'
                        }
                        all_stories.append(gdelt_story)
        except Exception as e:
            print(f"Error getting GDELT stories: {e}")
        
        # Select a random story
        if all_stories:
            lucky_story = random.choice(all_stories)
            return jsonify({
                'success': True,
                'story': lucky_story
            })
        else:
            return jsonify({
                'success': False,
                'error': f'No stories found for {continent}'
            }), 404
            
    except Exception as e:
        print(f"Error in /api/lucky/{continent}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
