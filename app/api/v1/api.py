"""API v1 router configuration.

This module sets up the main API router and includes all sub-routers for different
endpoints.
"""

from fastapi import APIRouter
from app.api.v1.chatbot import router as chatbot_router

api_router = APIRouter()

# Include routers
api_router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}