# app/db.py
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv
import os
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _connect(self):
        """Establish database connection with retry logic"""
        try:
            connection_string = os.getenv("MONGODB_URI")
            if not connection_string:
                raise ValueError("MONGODB_URI environment variable not set")
            
            self.client = MongoClient(
                connection_string,
                connectTimeoutMS=5000,
                socketTimeoutMS=30000,
                serverSelectionTimeoutMS=5000
            )
            
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[os.getenv("DB_NAME", "arborai")]
            
            print("✅ Successfully connected to MongoDB")
            self._create_indexes()
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected database error: {e}")
            raise

    def _create_indexes(self):
        """Create performance-optimized indexes"""
        try:
            # Marketplace indexes
            self.db.listings.create_index([("title", TEXT), ("description", TEXT)])
            self.db.listings.create_index([("category", ASCENDING)])
            self.db.listings.create_index([("price", ASCENDING)])
            
            # User indexes
            self.db.users.create_index([("email", ASCENDING)], unique=True)
            
            # Chat indexes
            self.db.chat_sessions.create_index([("user_id", ASCENDING)])
            self.db.chat_sessions.create_index([("last_updated", ASCENDING)])
            
            print("✅ Database indexes created/verified")
        except OperationFailure as e:
            print(f"⚠️ Index creation warning: {e}")

    def get_collection(self, collection_name: str):
        """Safely get a collection reference"""
        if not self.db:
            self._connect()
        return self.db[collection_name]

    def close_connection(self):
        """Clean up database connections"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")

# Singleton database instance
db_manager = DatabaseManager()

# Helper functions for common operations
def get_db():
    """Dependency for FastAPI routes"""
    return db_manager

def get_collection(collection_name: str):
    """Quick access to collections"""
    return db_manager.get_collection(collection_name)

def create_indexes():
    """Explicit index creation (called on startup)"""
    db_manager._create_indexes()

# Sample CRUD operations (extend as needed)
def insert_document(collection: str, document: dict) -> str:
    """Insert a single document"""
    col = get_collection(collection)
    result = col.insert_one(document)
    return str(result.inserted_id)

def find_documents(
    collection: str,
    query: dict,
    projection: Optional[dict] = None,
    limit: int = 0
) -> list:
    """Find multiple documents"""
    col = get_collection(collection)
    return list(col.find(query, projection).limit(limit))

# Test connection on import
if __name__ == "__main__":
    try:
        test_db = get_db()
        print("Database connection test successful!")
        print(f"Available collections: {test_db.db.list_collection_names()}")
    except Exception as e:
        print(f"Connection test failed: {e}")
    finally:
        db_manager.close_connection()