from flask import Flask, render_template
from blueprints.init_db import gdelt_bp
from blueprints.SQL_integration import sql_bp, get_index_page_news
import csv
import os
import json

#flask instance
app = Flask(__name__)

# Import and register the gdelt blueprint
app.register_blueprint(gdelt_bp)
app.register_blueprint(sql_bp)

def get_continent_style(continent):
    style_dict = {
        'Africa': 'bg-africa',
        'Americas': 'bg-americas',
        'Asia': 'bg-asia',
        'Europe': 'bg-europe',
        'Oceania': 'bg-oceania'
    }
    return style_dict.get(continent, '')

def get_recent_gdelt_events(limit=3):
    """Get recent GDELT events from CSV file"""
    csv_path = os.path.join(app.root_path, 'data', '20250613230000.export.csv')
    json_path = os.path.join(app.root_path, 'helper', 'countryToContinent.json')
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return []
    
    # Load country to continent mapping
    with open(json_path, 'r') as f:
        country_mapping = json.load(f)
    
    events = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            for row in reader:
                if len(row) > 51:  # Make sure row has enough columns
                    country_code = row[51]  # ActionGeo_CountryCode
                    continent = country_mapping.get(country_code, None)
                    
                    if continent:
                        events.append({
                            'country': country_code,
                            'continent': continent,
                            'title': f"Event between {row[27] or 'Unknown'} and {row[35] or 'Unknown'}",
                            'url': '#',
                            'goldstein': float(row[30]) if row[30] else 0,
                            'mentions': int(row[31]) if row[31] else 0
                        })
                        
                        if len(events) >= limit:
                            break
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return events

@app.route('/')
def index():
    news_stories = get_index_page_news()
    print(f"Debug: Found {len(news_stories)} events from CSV")
    return render_template("index.html", news_stories=news_stories, get_continent_style=get_continent_style)

# Add routes for each continent
@app.route('/africa-news')
def africa_news():
    events = get_index_page_news()  # Get events from CSV
    news_stories = [event for event in events if event['continent'] == 'Africa']
    return render_template('continent-news.html', continent='Africa', news_stories=news_stories, get_continent_style=get_continent_style)

@app.route('/americas-news')
def americas_news():
    events = get_index_page_news()
    news_stories = [event for event in events if event['continent'] == 'Americas']
    return render_template('continent-news.html', continent='Americas', news_stories=news_stories, get_continent_style=get_continent_style)

@app.route('/asia-news')
def asia_news():
    events = get_index_page_news()
    news_stories = [event for event in events if event['continent'] == 'Asia']
    return render_template('continent-news.html', continent='Asia', news_stories=news_stories, get_continent_style=get_continent_style)

@app.route('/europe-news')
def europe_news():
    events = get_index_page_news()
    news_stories = [event for event in events if event['continent'] == 'Europe']
    return render_template('continent-news.html', continent='Europe', news_stories=news_stories, get_continent_style=get_continent_style)

@app.route('/oceania-news')
def oceania_news():
    events = get_index_page_news()
    news_stories = [event for event in events if event['continent'] == 'Oceania']
    return render_template('continent-news.html', continent='Oceania', news_stories=news_stories, get_continent_style=get_continent_style)

if __name__=="__main__":
    app.run(debug=True)