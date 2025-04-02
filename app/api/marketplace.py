from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from bson import ObjectId
from app.db import get_db
from app.models.marketplace import ListingCreate, ListingResponse
from datetime import datetime
import os

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

# Image upload directory (configure for Azure Blob Storage in production)
UPLOAD_DIR = "uploads/listings"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/listings/", response_model=ListingResponse)
async def create_listing(
    listing_data: ListingCreate,
    images: List[UploadFile] = File(...),
    db=Depends(get_db)
):
    """Create a new tree/plant listing"""
    try:
        # Save images locally (replace with Azure Blob Storage in production)
        image_urls = []
        for img in images:
            file_path = f"{UPLOAD_DIR}/{ObjectId()}_{img.filename}"
            with open(file_path, "wb") as buffer:
                buffer.write(await img.read())
            image_urls.append(f"/{file_path}")
        
        # Prepare listing document
        listing = listing_data.dict()
        listing.update({
            "images": image_urls,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active"
        })
        
        # Insert into database
        result = db.listings.insert_one(listing)
        listing["_id"] = str(result.inserted_id)
        
        return listing
        
    except Exception as e:
        raise HTTPException(500, f"Failed to create listing: {str(e)}")

@router.get("/listings/", response_model=List[ListingResponse])
async def get_listings(
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    limit: int = 20,
    db=Depends(get_db)
):
    """Search marketplace listings with filters"""
    query = {}
    if category:
        query["category"] = category
    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price
    
    listings = db.listings.find(query).limit(limit)
    return [{"_id": str(l["_id"]), **l} for l in listings]

@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: str, db=Depends(get_db)):
    """Get detailed listing information"""
    listing = db.listings.find_one({"_id": ObjectId(listing_id)})
    if not listing:
        raise HTTPException(404, "Listing not found")
    listing["_id"] = str(listing["_id"])
    return listing