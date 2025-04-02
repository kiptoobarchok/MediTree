from fastapi import APIRouter, HTTPException, Depends
from app.db import get_db
from app.models.user import UserCreate, UserResponse
from bson import ObjectId
from datetime import datetime
import hashlib

router = APIRouter(prefix="/users", tags=["Users"])

def hash_password(password: str) -> str:
    """Basic password hashing (use proper auth in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate, db=Depends(get_db)):
    """Register a new user"""
    # Check if email exists
    if db.users.find_one({"email": user_data.email}):
        raise HTTPException(400, "Email already registered")
    
    user_doc = {
        **user_data.dict(exclude={"password"}),
        "hashed_password": hash_password(user_data.password),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "role": "user"  # or "admin", "nursery_owner" etc.
    }
    
    result = db.users.insert_one(user_doc)
    return {"_id": str(result.inserted_id), **user_doc}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db=Depends(get_db)):
    """Get user profile"""
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found")
    user["_id"] = str(user["_id"])
    return user

@router.get("/{user_id}/listings")
async def get_user_listings(user_id: str, db=Depends(get_db)):
    """Get all listings by a user"""
    listings = db.listings.find({"seller_id": ObjectId(user_id)})
    return [{"_id": str(l["_id"]), **l} for l in listings]