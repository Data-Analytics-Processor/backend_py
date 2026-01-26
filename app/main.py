"""
Minimal FastAPI main application entry point.
"""
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

load_dotenv()

app = FastAPI(title=settings.PROJECT_NAME)

# CORS (Critical for Flutter communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the chat router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"name": settings.PROJECT_NAME, "status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=5000, reload=True)