from app.db import get_db
from bson import ObjectId

def create_listing(listing_data: dict):
    db = get_db()
    result = db.listings.insert_one(listing_data)
    return str(result.inserted_id)

def get_listing(listing_id: str):
    db = get_db()
    listing = db.listings.find_one({"_id": ObjectId(listing_id)})
    listing["_id"] = str(listing["_id"])  # Convert ObjectId to string
    return listing

def search_listings(query: str = "", category: str = ""):
    db = get_db()
    filter = {}
    if query:
        filter["$text"] = {"$search": query}
    if category:
        filter["category"] = category
    
    return list(db.listings.find(filter).limit(20))