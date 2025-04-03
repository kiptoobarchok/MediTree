from app.db import get_db
from bson import ObjectId
from datetime import datetime

def add_message(session_id: str, sender: str, text: str):
    db = get_db()
    db.chat_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$push": {"messages": {"sender": sender, "text": text, "timestamp": datetime.utcnow()}},
            "$set": {"last_updated": datetime.utcnow()}
        }
    )

def get_chat_history(session_id: str):
    db = get_db()
    session = db.chat_sessions.find_one({"_id": ObjectId(session_id)})
    return session["messages"] if session else []