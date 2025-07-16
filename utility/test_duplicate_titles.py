from pymongo import MongoClient
from collections import Counter

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["news_world_database"]
collection = db["news_by_location"]

def find_duplicate_titles():
    # Get all titles
    titles = [doc.get('title', '').strip() for doc in collection.find({}, {'title': 1}) if doc.get('title')]
    title_counts = Counter(titles)
    duplicates = {title: count for title, count in title_counts.items() if count > 1}
    print(f"Total documents: {len(titles)}")
    print(f"Duplicate titles found: {len(duplicates)}")
    for title, count in duplicates.items():
        print(f"'{title}' appears {count} times")

if __name__ == "__main__":
    find_duplicate_titles() 