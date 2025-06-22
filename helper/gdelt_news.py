
from datetime import datetime, timedelta
import json
import time
import os
import requests
import pandas as pd
from .database import NewsDatabase
from .country_to_continent import country_to_continent

class GDELTNewsFetcher:
    def __init__(self):
        self.base_url = "https://api.gdeltproject.org/api/v2/geo/geo"
        # Use only countries with a continent mapping
        self.un_countries = list(country_to_continent.keys())
        self.db = NewsDatabase()
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

    def fetch_news_for_country(self, country, start_date=None, end_date=None):
        """
        Fetch news for a specific country using GDELT GEO 2.0 API
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')

        params = {
            'query': f'location:"{country}"',
            'mode': 'artlist',
            'format': 'json',
            'startdatetime': f'{start_date}000000',
            'enddatetime': f'{end_date}235959'
        }

        try:
            print(f"\nFetching news for {country}...")
            print(f"API URL: {self.base_url}")
            print(f"Parameters: {params}")
            
            response = requests.get(self.base_url, params=params, timeout=10)
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            
            # Print raw response for debugging
            print(f"Raw Response: {response.text[:200]}...")  # Print first 200 chars
            
            response.raise_for_status()
            data = response.json()
            
            if not data or 'articles' not in data:
                print(f"No articles found for {country}")
                return None
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for {country}: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response for {country}: {str(e)}")
            print(f"Response content: {response.text[:200]}...")  # Print first 200 chars
            return None

    def fetch_all_countries_news(self, start_date=None, end_date=None):
        """
        Fetch news for all UN member countries
        """
        all_news = {}
        
        for country in self.un_countries:
            news_data = self.fetch_news_for_country(country, start_date, end_date)
            if news_data:
                all_news[country] = news_data
                # Store in database
                self.db.add_news(country, news_data)
            time.sleep(2)  # Increased delay to avoid rate limiting
            
        return all_news

    def save_to_json(self, data, filename):
        """
        Save the fetched news data to a JSON file
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_to_csv(self, data, filename):
        """
        Convert and save the news data to a CSV file
        """
        rows = []
        for country, news in data.items():
            continent = country_to_continent.get(country, None)
            if news and 'articles' in news:
                for article in news['articles']:
                    row = {
                        'country': country,
                        'continent': continent,
                        'title': article.get('title', ''),
                        'url': article.get('url', ''),
                        'seendate': article.get('seendate', ''),
                        'domain': article.get('domain', ''),
                        'language': article.get('language', '')
                    }
                    rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False, encoding='utf-8')

    def export_database_to_csv(self, filename):
        """
        Export all news from the database to a CSV file
        """
        news_data = self.db.get_all_news()
        df = pd.DataFrame(news_data)
        df.to_csv(filename, index=False, encoding='utf-8')

def main():
    fetcher = GDELTNewsFetcher()
    
    # Fetch news for the last 24 hours
    start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    end_date = datetime.now().strftime('%Y%m%d')
    
    print("Starting to fetch news for mapped countries...")
    news_data = fetcher.fetch_all_countries_news(start_date, end_date)
    
    # Save the results
    fetcher.save_to_json(news_data, 'data/un_countries_news.json')
    fetcher.save_to_csv(news_data, 'data/un_countries_news_raw.csv')
    fetcher.export_database_to_csv('data/un_countries_news_db.csv')
    print("News data has been saved to JSON, CSV files and SQLite database, sorted by continent.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("An error occurred:")
        traceback.print_exc() 