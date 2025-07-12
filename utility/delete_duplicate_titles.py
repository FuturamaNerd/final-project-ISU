from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["news_world_database"]
collection = db["news_by_location"]

def has_ner_array(doc):
    entities = doc.get('entities')
    return isinstance(entities, list) and len(entities) > 0

def delete_duplicate_titles_keep_ner():
    pipeline = [
        {"$group": {
            "_id": "$title",
            "ids": {"$addToSet": "$_id"},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gt": 1}}}
    ]
    duplicates = list(collection.aggregate(pipeline))

    total_deleted = 0
    for group in duplicates:
        # Fetch all docs for this title
        docs = list(collection.find({"_id": {"$in": group["ids"]}}))
        # Try to find a doc with a non-empty NER array
        doc_to_keep = None
        for doc in docs:
            if has_ner_array(doc):
                doc_to_keep = doc
                break
        if not doc_to_keep:
            doc_to_keep = docs[0]  # fallback: keep the first
        ids_to_delete = [doc["_id"] for doc in docs if doc["_id"] != doc_to_keep["_id"]]
        if ids_to_delete:
            result = collection.delete_many({"_id": {"$in": ids_to_delete}})
            total_deleted += result.deleted_count
            print(f"Deleted {result.deleted_count} duplicates for title: {group['_id']}")
    print(f"Total duplicates deleted: {total_deleted}")

if __name__ == "__main__":
    delete_duplicate_titles_keep_ner() 