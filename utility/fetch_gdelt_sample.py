import sqlite3
import random
import json
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
DB_PATH = "gdelt_events.db"
COUNTRY_TO_CONTINENT_PATH = os.path.join(os.path.dirname(__file__), "countryToContinent.json")

# --- LOAD COUNTRY TO CONTINENT MAPPING ---
with open(COUNTRY_TO_CONTINENT_PATH, "r", encoding="utf-8") as f:
    COUNTRY_TO_CONTINENT = json.load(f)

def map_country_to_continent(country_code):
    return COUNTRY_TO_CONTINENT.get(country_code, "Unknown")

# --- SETUP SQLITE ---
def setup_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS gdelt_events (
            event_id TEXT PRIMARY KEY,
            date TEXT,
            event_code TEXT,
            goldstein REAL,
            actor1_name TEXT,
            actor1_country TEXT,
            actor2_name TEXT,
            actor2_country TEXT,
            latitude REAL,
            longitude REAL,
            location_name TEXT,
            continent TEXT,
            source_url TEXT
        )
    ''')
    conn.commit()
    return conn

# --- SAMPLE DATA GENERATION ---
def generate_sample_gdelt_events(num_events=120):
    # Sample event codes and their descriptions
    event_codes = [
        ('01', 'MAKE PUBLIC STATEMENT'),
        ('02', 'APPEAL'),
        ('03', 'EXPRESS INTENT TO COOPERATE'),
        ('04', 'CONSULT'),
        ('05', 'ENGAGE IN DIPLOMATIC COOPERATION'),
        ('06', 'ENGAGE IN MATERIAL COOPERATION'),
        ('07', 'PROVIDE AID'),
        ('08', 'YIELD'),
        ('09', 'INVESTIGATE'),
        ('10', 'DEMAND'),
        ('11', 'DISAPPROVE'),
        ('12', 'REJECT'),
        ('13', 'THREATEN'),
        ('14', 'PROTEST'),
        ('15', 'EXHIBIT FORCE POSTURE')
    ]
    
    # Sample countries with their coordinates
    countries = [
        ('US', 'United States', 39.8283, -98.5795),
        ('CA', 'Canada', 56.1304, -106.3468),
        ('BR', 'Brazil', -14.2350, -51.9253),
        ('MX', 'Mexico', 23.6345, -102.5528),
        ('AR', 'Argentina', -38.4161, -63.6167),
        ('GB', 'United Kingdom', 55.3781, -3.4360),
        ('DE', 'Germany', 51.1657, 10.4515),
        ('FR', 'France', 46.2276, 2.2137),
        ('IT', 'Italy', 41.8719, 12.5674),
        ('ES', 'Spain', 40.4637, -3.7492),
        ('CN', 'China', 35.8617, 104.1954),
        ('JP', 'Japan', 36.2048, 138.2529),
        ('IN', 'India', 20.5937, 78.9629),
        ('KR', 'South Korea', 35.9078, 127.7669),
        ('AU', 'Australia', -25.2744, 133.7751),
        ('ZA', 'South Africa', -30.5595, 22.9375),
        ('EG', 'Egypt', 26.8206, 30.8025),
        ('NG', 'Nigeria', 9.0820, 8.6753),
        ('KE', 'Kenya', -0.0236, 37.9062)
    ]
    
    # Sample actor names
    actor_names = [
        'Government', 'President', 'Prime Minister', 'Minister', 'Official',
        'UN', 'NATO', 'EU', 'Organization', 'Company', 'Corporation',
        'Military', 'Police', 'Protesters', 'Activists', 'Citizens',
        'Media', 'Journalists', 'Reporters', 'News Agency'
    ]
    
    # Sample news sources
    news_sources = [
        'https://www.reuters.com/article/',
        'https://www.bbc.com/news/',
        'https://www.cnn.com/',
        'https://www.nytimes.com/',
        'https://www.washingtonpost.com/',
        'https://www.theguardian.com/',
        'https://www.lemonde.fr/',
        'https://www.spiegel.de/',
        'https://www.corriere.it/',
        'https://www.elpais.com/'
    ]
    
    events = []
    base_date = datetime.now() - timedelta(days=7)
    
    for i in range(num_events):
        # Generate random event data
        event_date = base_date + timedelta(hours=random.randint(0, 168))
        event_code, event_desc = random.choice(event_codes)
        goldstein = random.uniform(-10, 10)
        
        # Random country and coordinates
        country_code, country_name, lat, lon = random.choice(countries)
        # Add some random variation to coordinates
        lat += random.uniform(-2, 2)
        lon += random.uniform(-2, 2)
        
        # Random actors
        actor1 = random.choice(actor_names)
        actor2 = random.choice(actor_names)
        
        # Random source URL
        source_url = random.choice(news_sources) + f"event-{random.randint(1000, 9999)}"
        
        # Generate event ID
        event_id = f"GDELT_{int(event_date.timestamp())}_{random.randint(1000, 9999)}"
        
        # Map country to continent
        continent = map_country_to_continent(country_code)
        
        events.append({
            'event_id': event_id,
            'date': event_date.strftime('%Y%m%d'),
            'event_code': event_code,
            'goldstein': round(goldstein, 2),
            'actor1_name': actor1,
            'actor1_country': country_code,
            'actor2_name': actor2,
            'actor2_country': random.choice(countries)[0],
            'latitude': round(lat, 4),
            'longitude': round(lon, 4),
            'location_name': f"{country_name}, {random.choice(['Capital', 'Major City', 'Region'])}",
            'continent': continent,
            'source_url': source_url
        })
    
    return events

def store_sample_events():
    conn = setup_db()
    c = conn.cursor()
    
    print("Generating sample GDELT events...")
    events = generate_sample_gdelt_events(120)
    
    for event in events:
        c.execute('''
            INSERT OR REPLACE INTO gdelt_events (
                event_id, date, event_code, goldstein, actor1_name, actor1_country, actor2_name, actor2_country,
                latitude, longitude, location_name, continent, source_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event['event_id'], event['date'], event['event_code'], event['goldstein'],
            event['actor1_name'], event['actor1_country'], event['actor2_name'], event['actor2_country'],
            event['latitude'], event['longitude'], event['location_name'], event['continent'], event['source_url']
        ))
    
    conn.commit()
    conn.close()
    print(f"Stored {len(events)} sample GDELT events in SQLite.")

if __name__ == "__main__":
    store_sample_events()
    print("Sample data generation complete!") 