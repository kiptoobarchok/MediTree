# app/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ArborAI",
    description="AI-Powered Tree Planting Assistant & Marketplace",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
from app.db import get_db
db = get_db()

# AI Services Setup
from app.core.llm import chat_llm, image_llm

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates setup
templates = Jinja2Templates(directory="templates")

# Import routers
from app.api import (
    marketplace,
    chat,
    images,
    users
)

# Include API routes
app.include_router(marketplace.router, prefix="/api/marketplace", tags=["Marketplace"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

# Frontend Routes
@app.get("/", include_in_schema=False)
async def home(request: Request):
    """Render homepage"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/marketplace", include_in_schema=False)
async def marketplace_page(request: Request):
    """Render marketplace page"""
    listings = list(db.listings.find().limit(20))
    return templates.TemplateResponse(
        "marketplace.html",
        {"request": request, "listings": listings}
    )

@app.get("/chat", include_in_schema=False)
async def chat_page(request: Request):
    """Render chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})

# Health Check
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected" if db else "disconnected",
            "openai": "ready" if chat_llm else "unavailable"
        }
    }

# Error Handlers
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# Startup Event
@app.on_event("startup")
async def startup():
    """Initialize application services"""
    # Create database indexes
    from app.db import create_indexes
    create_indexes()
    
    # Warm up AI models
    if os.getenv("WARMUP_AI", "false").lower() == "true":
        chat_llm.invoke("Ping")