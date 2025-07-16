from pymongo import MongoClient
import requests
from datetime import datetime
from config import NEWS_API_KEY

def fetch_and_store_top_100():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'apiKey': NEWS_API_KEY,
        'pageSize': 100,
        'language': 'en'
    }
    response = requests.get(url, params=params)
    data = response.json()
    articles = data.get('articles', [])
    client = MongoClient("mongodb://localhost:27017/")
    db = client["news_world_database"]
    for article in articles:
        article['saved_at'] = datetime.utcnow()
        db.news_by_location.insert_one(article)
    print(f"Saved {len(articles)} articles to MongoDB.")

if __name__ == "__main__":
    fetch_and_store_top_100()
