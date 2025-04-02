from fastapi import APIRouter, HTTPException, Depends
from app.db import get_db
from app.core.llm import chat_llm
from bson import ObjectId
from datetime import datetime
from typing import Optional
import json

router = APIRouter(prefix="/chat", tags=["Chatbot"])

@router.post("/sessions/")
async def create_chat_session(
    user_id: str,
    initial_message: Optional[str] = None,
    db=Depends(get_db)
):
    """Start a new chat session"""
    session_data = {
        "user_id": ObjectId(user_id),
        "messages": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    if initial_message:
        session_data["messages"].append({
            "sender": "user",
            "text": initial_message,
            "timestamp": datetime.utcnow()
        })
    
    result = db.chat_sessions.insert_one(session_data)
    return {"session_id": str(result.inserted_id)}

@router.post("/sessions/{session_id}/messages")
async def add_message(
    session_id: str,
    message: str,
    db=Depends(get_db)
):
    """Process user message and get AI response"""
    # 1. Save user message
    user_msg = {
        "sender": "user",
        "text": message,
        "timestamp": datetime.utcnow()
    }
    
    db.chat_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$push": {"messages": user_msg},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    # 2. Get chat history for context
    session = db.chat_sessions.find_one({"_id": ObjectId(session_id)})
    chat_history = "\n".join(
        f"{msg['sender']}: {msg['text']}" 
        for msg in session["messages"][-5:]  # Last 5 messages as context
    )
    
    # 3. Get AI response
    prompt = f"""
    Chat History:
    {chat_history}
    
    As ArborAI, provide knowledgeable but friendly advice about tree care:
    User: {message}
    ArborAI:"""
    
    try:
        ai_response = chat_llm.invoke(prompt).content
        
        # 4. Save AI response
        ai_msg = {
            "sender": "assistant",
            "text": ai_response,
            "timestamp": datetime.utcnow()
        }
        
        db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$push": {"messages": ai_msg},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {"response": ai_response}
    
    except Exception as e:
        raise HTTPException(500, f"AI service error: {str(e)}")