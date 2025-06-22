import sqlite3
from datetime import datetime
import os
import json

class NewsDatabase:
    def __init__(self, db_path='data/news.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create countries table with continent
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            continent TEXT
        )
        ''')

        # Create news table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            seen_date TEXT,
            domain TEXT,
            language TEXT,
            created_at TEXT,
            FOREIGN KEY (country_id) REFERENCES countries (id)
        )
        ''')

        conn.commit()
        conn.close()

    def _load_country_mapping(self):
        """Load country to continent mapping from JSON file"""
        json_path = os.path.join(os.path.dirname(__file__), 'countryToContinent.json')
        with open(json_path, 'r') as f:
            return json.load(f)

    def add_country(self, country_name):
        """Add a country to the database if it doesn't exist, with continent"""
        country_mapping = self._load_country_mapping()
        continent = country_mapping.get(country_name, None)
        print(f"Debug: Adding country '{country_name}' with continent '{continent}'")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO countries (name, continent) VALUES (?, ?)', (country_name, continent))
        conn.commit()
        cursor.execute('SELECT id FROM countries WHERE name = ?', (country_name,))
        country_id = cursor.fetchone()[0]
        conn.close()
        return country_id

    def add_news(self, country_name, news_items):
        """Add news items for a country"""
        if not news_items or 'articles' not in news_items:
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        country_id = self.add_country(country_name)
        current_time = datetime.now().isoformat()
        for article in news_items['articles']:
            try:
                cursor.execute('''
                INSERT OR IGNORE INTO news 
                (country_id, title, url, seen_date, domain, language, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    country_id,
                    article.get('title', ''),
                    article.get('url', ''),
                    article.get('seendate', ''),
                    article.get('domain', ''),
                    article.get('language', ''),
                    current_time
                ))
            except sqlite3.Error as e:
                print(f"Error inserting news for {country_name}: {str(e)}")
        conn.commit()
        conn.close()

    def get_all_news(self):
        """Retrieve all news from the database, including continent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT c.name as country, c.continent, n.title, n.url, n.seen_date, n.domain, n.language
        FROM news n
        JOIN countries c ON n.country_id = c.id
        ORDER BY n.seen_date DESC
        ''')
        columns = [description[0] for description in cursor.description]
        news_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return news_data

    def get_news_by_continent(self, continent):
        """Retrieve news for a specific continent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT c.name as country, c.continent, n.title, n.url, n.seen_date, n.domain, n.language
        FROM news n
        JOIN countries c ON n.country_id = c.id
        WHERE c.continent = ?
        ORDER BY n.seen_date DESC
        ''', (continent,))
        columns = [description[0] for description in cursor.description]
        news_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return news_data

    def get_most_recent_news(self, limit=3):
        """Retrieve the most recent news from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT c.name as country, c.continent, n.title, n.url, n.seen_date, n.domain, n.language
        FROM news n
        JOIN countries c ON n.country_id = c.id
        ORDER BY n.created_at DESC
        LIMIT ?
        ''', (limit,))
        columns = [description[0] for description in cursor.description]
        news_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return news_data 