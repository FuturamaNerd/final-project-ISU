from flask import Flask, render_template
from flask_pymongo import PyMongo
from datetime import datetime

#flask instance
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/news_world_database"
mongo = PyMongo(app)

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
    """Render news for a specific continent using dummy data from MongoDB."""
    try:
        # Get news stories for the specified continent from dummy_news collection
        news_stories = list(mongo.db.dummy_news.find({'continent': continent}))
        
        # Debug: Print the raw data to see what we're getting
        if news_stories:
            print(f"DEBUG: Found {len(news_stories)} stories for {continent}")
            print(f"DEBUG: First story raw data:")
            first_story = news_stories[0]
            for key, value in first_story.items():
                print(f"  {key}: {value}")
        else:
            print(f"DEBUG: No stories found for {continent}")
        
        # Convert MongoDB ObjectId to string for JSON serialization
        for story in news_stories:
            story['_id'] = str(story['_id'])
        
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

if __name__=="__main__":
    app.run(debug=True)