from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["news_world_database"]
collection = db["news_by_location"]

def count_articles_with_ner():
    # Find documents where 'entities' exists and is a non-empty array
    query = {'entities': {'$exists': True, '$type': 'array', '$ne': []}}
    count = collection.count_documents(query)
    print(f"Documents with non-empty NER 'entities' array: {count}")
    # Optionally, print a few sample titles
    for doc in collection.find(query, {'title': 1}).limit(5):
        print(f"Sample title: {doc.get('title', 'No title')}")

if __name__ == "__main__":
    count_articles_with_ner() 