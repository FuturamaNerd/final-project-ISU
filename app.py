from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import sqlite3
from datetime import datetime
from utility.ner_processor import ner_processor
from blueprints import init_app

#flask instance
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/news_world_database"
mongo = PyMongo(app)

# Initialize blueprints
init_app(app, mongo)

#route decorator
@app.route('/')
def index():
    """Render index page with real news story and map marker."""
    try:
        # Get the real news story from news_by_location collection
        real_story = mongo.db.news_by_location.find_one()
        
        # If no story exists, create a sample one
        if not real_story:
            print("📝 Creating sample news story...")
            sample_story = {
                'title': 'Global Climate Summit Reaches Historic Agreement',
                'description': 'World leaders have agreed on ambitious new targets to reduce carbon emissions by 2030.',
                'url': 'https://news.example.com/climate-summit-2025',
                'urlToImage': 'https://images.example.com/climate-summit.jpg',
                'publishedAt': '2025-06-28T10:00:00Z',
                'content': 'The landmark agreement includes commitments from all major economies...',
                'source': {
                    'id': 'reuters',
                    'name': 'Reuters'
                },
                'source_country': 'US',
                'continent': 'Americas',
                'saved_at': datetime.utcnow()
            }
            
            # Insert the sample story
            result = mongo.db.news_by_location.insert_one(sample_story)
            real_story = sample_story
            real_story['_id'] = str(result.inserted_id)
            print(f"✅ Created sample story with ID: {result.inserted_id}")
        
        # Process with NER if not already processed
        if 'extracted_locations' not in real_story:
            real_story = ner_processor.process_article(real_story)
            # Update the database with NER results
            if '_id' in real_story:
                article_id = real_story.pop('_id', None)
                if article_id and not isinstance(article_id, str):
                    mongo.db.news_by_location.update_one(
                        {'_id': article_id},
                        {'$set': {
                            'extracted_locations': real_story.get('extracted_locations', []),
                            'location_count': real_story.get('location_count', 0),
                            'primary_location': real_story.get('primary_location'),
                            'ner_processed_at': datetime.utcnow()
                        }}
                    )
                    real_story['_id'] = str(article_id)
        
        # Convert MongoDB ObjectId to string
        if '_id' in real_story and not isinstance(real_story['_id'], str):
            real_story['_id'] = str(real_story['_id'])
        
        # Get country coordinates
        country_coords = get_country_coordinates(real_story.get('source_country', 'US'))
        
        return render_template('index.html', 
                             real_story=real_story,
                             country_coords=country_coords)
    except Exception as e:
        print(f"Error fetching real story: {e}")
        return render_template('index.html', 
                             real_story=None,
                             country_coords=None)

def get_country_coordinates(country_code):
    """Get approximate coordinates for a country code."""
    # Basic coordinates for major countries
    coords = {
        'US': [39.8283, -98.5795],  # Center of USA
        'CA': [56.1304, -106.3468], # Center of Canada
        'BR': [-14.2350, -51.9253], # Center of Brazil
        'MX': [23.6345, -102.5528], # Center of Mexico
        'AR': [-38.4161, -63.6167], # Center of Argentina
        'CL': [-35.6751, -71.5430], # Center of Chile
        'CO': [4.5709, -74.2973],   # Center of Colombia
        'PE': [-9.1900, -75.0152],  # Center of Peru
        'VE': [6.4238, -66.5897],   # Center of Venezuela
        'AU': [-25.2744, 133.7751], # Center of Australia
        'NZ': [-40.9006, 174.8860], # Center of New Zealand
        'FJ': [-17.7134, 178.0650], # Center of Fiji
        'PG': [-6.3150, 143.9555],  # Center of Papua New Guinea
        'WS': [-13.7590, -172.1046], # Center of Samoa
        'GB': [55.3781, -3.4360],   # Center of UK
        'DE': [51.1657, 10.4515],   # Center of Germany
        'FR': [46.2276, 2.2137],    # Center of France
        'IT': [41.8719, 12.5674],   # Center of Italy
        'ES': [40.4637, -3.7492],   # Center of Spain
        'CN': [35.8617, 104.1954],  # Center of China
        'JP': [36.2048, 138.2529],  # Center of Japan
        'IN': [20.5937, 78.9629],   # Center of India
        'KR': [35.9078, 127.7669],  # Center of South Korea
        'ZA': [-30.5595, 22.9375],  # Center of South Africa
        'EG': [26.8206, 30.8025],   # Center of Egypt
        'NG': [9.0820, 8.6753],     # Center of Nigeria
        'KE': [-0.0236, 37.9062],   # Center of Kenya
    }
    
    return coords.get(country_code, [39.8283, -98.5795])  # Default to US if not found

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/continent/<continent>')
def continent_news(continent):
    """Render news for a specific continent using coordinate-based filtering."""
    try:
        import json
        
        # Load continent bounding boxes
        try:
            with open('continentBoundingBoxes.json', 'r', encoding='utf-8') as f:
                continent_boxes = json.load(f)
        except FileNotFoundError:
            print(f"❌ continentBoundingBoxes.json not found")
            return render_template('[continent]-news.html', 
                                 continent=continent, 
                                 news_stories=[])
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing continentBoundingBoxes.json: {e}")
            return render_template('[continent]-news.html', 
                                 continent=continent, 
                                 news_stories=[])
        except Exception as e:
            print(f"❌ Error loading continentBoundingBoxes.json: {e}")
            return render_template('[continent]-news.html', 
                                 continent=continent, 
                                 news_stories=[])
        
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
            print(f"❌ Continent '{continent}' not found in bounding boxes")
            return render_template('[continent]-news.html', 
                                 continent=continent, 
                                 news_stories=[])
        
        bounds = continent_boxes[target_continent]
        print(f"🔍 Filtering for {continent} using bounds: {bounds}")
        
        news_stories = []
        
        # Get NewsAPI events from MongoDB using coordinate filtering
        try:
            # Get all NewsAPI articles with coordinates
            all_newsapi = list(mongo.db.news_by_location.find({
                '$and': [
                    {'latitude': {'$exists': True, '$ne': None}},
                    {'longitude': {'$exists': True, '$ne': None}}
                ]
            }))
            
            print(f"📊 Found {len(all_newsapi)} NewsAPI articles with coordinates")
            
            # Filter by continent using coordinates
            continent_newsapi = []
            for story in all_newsapi:
                lat = story.get('latitude')
                lon = story.get('longitude')
                
                if lat is not None and lon is not None:
                    # Check if coordinates fall within continent bounds
                    if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                        bounds['lon_min'] <= lon <= bounds['lon_max']):
                        continent_newsapi.append(story)
                        print(f"  ✅ {continent}: {lat}, {lon} - {story.get('title', 'No title')[:50]}...")
                    else:
                        print(f"  ❌ {continent}: {lat}, {lon} - OUT OF BOUNDS")
            
            # Take up to 9 NewsAPI stories
            continent_newsapi = continent_newsapi[:9]
            
            # Convert to template format
            for story in continent_newsapi:
                story['_id'] = str(story['_id'])
                story['data_source'] = 'newsapi'
                
                # Debug: Print the actual structure of a NewsAPI story
                if len(continent_newsapi) == 1:  # Only print for first story to avoid spam
                    print(f"🔍 DEBUG NewsAPI story structure:")
                    for key, value in story.items():
                        if key != '_id':
                            print(f"  {key}: {str(value)[:100]}...")
                
                # Ensure proper structure for template - NewsAPI data is at root level
                story['source'] = {
                    'title': story.get('title', 'No Title'),
                    'description': story.get('description', 'No description'),
                    'url': story.get('url', ''),
                    'urlToImage': story.get('urlToImage', ''),
                    'author': story.get('author', ''),
                    'publishedAt': story.get('publishedAt', '')
                }
                news_stories.append(story)
            
            print(f"✅ Found {len(continent_newsapi)} NewsAPI stories for {continent}")
                
        except Exception as e:
            print(f"Error accessing MongoDB for {continent}: {e}")
        
        # Get GDELT events from SQLite using coordinate filtering
        try:
            conn = sqlite3.connect('gdelt_events.db')
            c = conn.cursor()
            
            # Query GDELT events with coordinates
            gdelt_query = '''
                SELECT event_id, date, event_code, goldstein, actor1_name, actor1_country, 
                       actor2_name, actor2_country, latitude, longitude, location_name, 
                       continent, source_url, translated_title, translated_content, 
                       source_language, target_language, translation_confidence, 
                       sentiment_score, sentiment_magnitude, num_mentions, num_sources, 
                       avg_tone, event_root_code, event_base_code, quad_class
                FROM gdelt_events 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            '''
            
            all_gdelt = c.execute(gdelt_query).fetchall()
            conn.close()
            
            # Filter GDELT events by continent using coordinates
            continent_gdelt = []
            for story in all_gdelt:
                lat = story[8]  # latitude
                lon = story[9]  # longitude
                
                if lat is not None and lon is not None:
                    # Check if coordinates fall within continent bounds
                    if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                        bounds['lon_min'] <= lon <= bounds['lon_max']):
                        continent_gdelt.append(story)
            
            # Take up to 9 GDELT stories
            continent_gdelt = continent_gdelt[:9]
            
            # Convert GDELT data to template format
            for story in continent_gdelt:
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
                    'data_source': 'gdelt',
                    'source': {
                        'title': story[13] if story[13] else f'GDELT Event {story[0]}',
                        'description': story[14][:200] + '...' if story[14] and len(story[14]) > 200 else (story[14] or 'No description available'),
                        'url': story[12] or '#',
                        'urlToImage': '',
                        'author': f'GDELT - {story[4]}' if story[4] else 'GDELT',
                        'publishedAt': story[1] if story[1] else ''
                    }
                }
                news_stories.append(gdelt_story)
            
            print(f"✅ Found {len(continent_gdelt)} GDELT stories for {continent}")
                
        except Exception as e:
            print(f"Error accessing SQLite for {continent}: {e}")
        
        # Limit to 9 stories total (or all if less than 9)
        news_stories = news_stories[:9]
        
        print(f"🎯 Total stories for {continent}: {len(news_stories)}")
        
        return render_template('[continent]-news.html', 
                             continent=continent, 
                             news_stories=news_stories)
    except Exception as e:
        print(f"Error fetching news for {continent}: {e}")
        return render_template('[continent]-news.html', 
                             continent=continent, 
                             news_stories=[])

@app.route('/americas')
def americas_news():
    """Direct route for Americas news."""
    return continent_news('Americas')

@app.route('/oceania')
def oceania_news():
    """Direct route for Oceania news."""
    return continent_news('Oceania')

@app.route('/europe')
def europe_news():
    """Direct route for Europe news."""
    return continent_news('Europe')

@app.route('/asia')
def asia_news():
    """Direct route for Asia news."""
    return continent_news('Asia')

@app.route('/africa')
def africa_news():
    """Direct route for Africa news."""
    return continent_news('Africa')

@app.route('/api/articles/locations')
def get_articles_with_locations():
    """API endpoint to get articles with location information."""
    try:
        # Get articles that have been processed with NER
        articles = list(mongo.db.news_by_location.find({'extracted_locations': {'$exists': True}}))
        
        # Convert ObjectIds to strings
        for article in articles:
            article['_id'] = str(article['_id'])
        
        return jsonify({
            'success': True,
            'articles': articles,
            'count': len(articles)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/articles/search')
def search_articles_by_location():
    """API endpoint to search articles by location."""
    location = request.args.get('location', '').strip()
    
    if not location:
        return jsonify({
            'success': False,
            'error': 'Location parameter is required'
        }), 400
    
    try:
        # Get all articles
        articles = list(mongo.db.news_by_location.find())
        
        # Process articles if needed
        processed_articles = []
        for article in articles:
            if 'extracted_locations' not in article:
                processed_article = ner_processor.process_article(article)
                processed_articles.append(processed_article)
            else:
                processed_articles.append(article)
        
        # Find matching articles
        matching_articles = []
        location_lower = location.lower()
        for article in processed_articles:
            locations = article.get('extracted_locations', [])
            for loc in locations:
                if location_lower in loc['text'].lower() or loc['text'].lower() in location_lower:
                    matching_articles.append(article)
                    break
        
        # Convert ObjectIds to strings
        for article in matching_articles:
            if '_id' in article:
                article['_id'] = str(article['_id'])
        
        return jsonify({
            'success': True,
            'articles': matching_articles,
            'count': len(matching_articles),
            'search_term': location
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ner/process')
def process_articles_with_ner():
    """API endpoint to process all articles with NER."""
    try:
        # Get all articles
        articles = list(mongo.db.news_by_location.find())
        
        if not articles:
            return jsonify({
                'success': False,
                'error': 'No articles found in database'
            }), 404
        
        # Process articles with NER
        processed_articles = ner_processor.process_multiple_articles(articles)
        
        # Update articles in database
        updated_count = 0
        for article in processed_articles:
            article_id = article.pop('_id', None)
            if article_id:
                result = mongo.db.news_by_location.update_one(
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
        
        # Calculate basic statistics
        total_articles = len(processed_articles)
        articles_with_locations = sum(1 for article in processed_articles if article.get('location_count', 0) > 0)
        total_locations = sum(article.get('location_count', 0) for article in processed_articles)
        
        stats = {
            'total_articles': total_articles,
            'articles_with_locations': articles_with_locations,
            'total_locations_found': total_locations
        }
        
        return jsonify({
            'success': True,
            'processed_count': updated_count,
            'total_articles': len(articles),
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/locations')
def locations_view():
    """Display articles with their extracted location information."""
    try:
        # Get articles that have been processed with NER
        articles = list(mongo.db.news_by_location.find({'extracted_locations': {'$exists': True}}))
        
        # Convert ObjectIds to strings
        for article in articles:
            article['_id'] = str(article['_id'])
        
        # Calculate basic statistics
        total_articles = len(articles)
        articles_with_locations = sum(1 for article in articles if article.get('location_count', 0) > 0)
        total_locations = sum(article.get('location_count', 0) for article in articles)
        
        stats = {
            'total_articles': total_articles,
            'articles_with_locations': articles_with_locations,
            'total_locations_found': total_locations
        }
        
        return render_template('locations.html', 
                             articles=articles,
                             stats=stats)
    except Exception as e:
        print(f"Error fetching articles with locations: {e}")
        return render_template('locations.html', 
                             articles=[],
                             stats={})

if __name__=="__main__":
    app.run(debug=True)