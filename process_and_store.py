from pymongo import MongoClient
from utility.ner_processor import process_and_store_articles_with_ner

client = MongoClient("mongodb://localhost:27017/")
db = client["news_world_database"]

print("collections:", db.list_collection_names())
articles = list(db.news_by_location.find())
process_and_store_articles_with_ner(articles, "mongodb://localhost:27017/news_world_database")